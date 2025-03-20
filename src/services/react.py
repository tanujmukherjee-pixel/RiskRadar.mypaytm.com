from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
import os
from llama_index.core import PromptTemplate

react_system_header_str = """\
## Tools
You have access to a wide variety of tools. You are responsible for using
the tools in any sequence you deem appropriate to complete the task at hand.
This may require breaking the task into subtasks and using different tools
to complete each subtask.

You have access to the following tools:
{tool_desc}

## Output Format
To answer the question, please use the following format.

Thought: I need to use a tool to help me answer the question.
Action: tool name (one of {tool_names}) if using a tool.
Action Input: the input to the tool, in a JSON format representing the kwargs (e.g. {{"input": "hello world", "num_beams": 5}})

Thought: I will proceed to fetch more information.
Action: tool name (one of {tool_names}) if using a tool.
Action Input: the input to the tool, in a JSON format representing the kwargs (e.g. {{"input": "hello world", "num_beams": 5}})

Thought: I need to fetch more information.
Action: tool name (one of {tool_names}) if using a tool.
Action Input: the input to the tool, in a JSON format representing the kwargs (e.g. {{"input": "hello world", "num_beams": 5}})

Please use a valid JSON format for the Action Input. Do NOT do this {{'input': 'hello world', 'num_beams': 5}}.

If this format is used, the user will respond in the following format:

Observation: response


You should keep repeating the above format (Thought and Action) until you have enough information
to answer the question without using any more tools or dont want to proceed to fetch more information. At that point, you MUST respond
in the one of the following two formats only if you do not want to perform any action or doing some analysis or want to proceed to fetch more information:

Thought: I have all the information I need.
Answer: [your answer here]


Thought: I cannot answer the question with the provided tools.
Answer: Sorry, I cannot answer your query.

<IMPORTANT>
Do not respond with an answer if you want to perform any action or doing some analysis. Always respond with Thought and Action. If meanwhile want to communicate with user, use Thought.
</IMPORTANT>

## Additional Rules
- You MUST obey the function signature of each tool. Do NOT pass in no arguments if the function expects arguments.

## Current Conversation
Below is the current conversation consisting of interleaving human and assistant messages.

"""

def react_query_engine(system_prompt, approach_prompt, output_prompt, tools):
    """
    Creates and returns a ReAct agent that utilizes both the query engine and Kibana logs fetcher.
    """
    llm = OpenAI(
        model=os.environ.get("LLM_MODEL"),
        api_key=os.environ.get("OPENAI_API_KEY"),
        api_base=os.environ.get("OPENAI_API_BASE")
    )

    callbacks = []
    if os.environ.get("ENABLE_CALLBACK") in ["true", "True", "1", True]:
        from llama_index.core.callbacks import CallbackManager
        from opik.integrations.llama_index import LlamaIndexCallbackHandler

        opik_callback_handler = LlamaIndexCallbackHandler()
        callbacks.append(opik_callback_handler)

    # Create the ReAct agent
    agent = ReActAgent.from_tools(
        tools,
        llm=llm,
        verbose=True,
        max_iterations=50,
        callback_manager=CallbackManager(callbacks) if callbacks else None
    )

    react_system_prompt = PromptTemplate(
        template=system_prompt + "\n\n## Approach\n\n" + approach_prompt + "\n\n## Final Answer\n\n" + output_prompt + "\n\n" + react_system_header_str
    )

    agent.update_prompts({"agent_worker:system_prompt": react_system_prompt})

    agent.reset()

    if os.environ.get("ENABLE_PROMPT"):
        prompt_dict = agent.get_prompts()
        for k, v in prompt_dict.items():
            print(f"Prompt: {k}\n\nValue: {v.template}")
    return agent
