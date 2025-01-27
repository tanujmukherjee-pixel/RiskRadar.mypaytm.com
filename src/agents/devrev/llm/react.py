from llama_index.core.agent import ReActAgent
from llama_index.core.tools import QueryEngineTool, FunctionTool, ToolMetadata
from llama_index.llms.openai import OpenAI
import os
from .query import query_engine
from ..tools.druid import execute_query_pulse, fetch_all_segments, get_all_funnels, fetch_base_query
from llama_index.core import PromptTemplate

react_system_header_str = """\

You are an RCA (Root Cause Analysis) agent designed to identify the root cause of issues. Your capabilities include answering questions, summarizing data, and performing in-depth analyses.

## Approach

1. Identify all relevant funnels related to the user's concern.
2. Fetch the base query for each funnel.
3. Determine all possible segments for the concern.
4. Execute base query with each segment.
5. Analyze the results to identify the most relevant segment or pinpoint the root cause.

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


Please ALWAYS start with a Thought.

Please use a valid JSON format for the Action Input. Do NOT do this {{'input': 'hello world', 'num_beams': 5}}.

If this format is used, the user will respond in the following format:

Observation: tool response


You should keep repeating the above format until you have enough information
to answer the question without using any more tools. At that point, you MUST respond
in the one of the following two formats:

Thought: I can answer without using any more tools.
Answer: [your answer here]


Thought: I cannot answer the question with the provided tools.
Answer: Sorry, I cannot answer your query.


## Additional Rules
- The answer MUST contain a sequence of bullet points that explain how you arrived at the answer. This can include aspects of the previous conversation history.
- You MUST obey the function signature of each tool. Do NOT pass in no arguments if the function expects arguments.

## Current Conversation
Below is the current conversation consisting of interleaving human and assistant messages.

"""

def react_query_engine():
    """
    Creates and returns a ReAct agent that utilizes both the query engine and Kibana logs fetcher.
    """
    llm = OpenAI(
        model="gpt-4o",
        api_key="REDACTED_OPENAI_KEY"
    )

    react_system_prompt = PromptTemplate(react_system_header_str)

    # Set up the query engine tool
    query_engine_tool = QueryEngineTool(query_engine=query_engine, metadata=ToolMetadata(name="Docs", description="Tool to perform any other queries"))

    druid_tool = FunctionTool.from_defaults(fn=execute_query_pulse)
    segments_tool = FunctionTool.from_defaults(fn=fetch_all_segments)
    funnels_tool = FunctionTool.from_defaults(fn=get_all_funnels)
    base_query_tool = FunctionTool.from_defaults(fn=fetch_base_query)

    # Create the ReAct agent
    agent = ReActAgent.from_tools([druid_tool, segments_tool, funnels_tool, base_query_tool], llm=llm, verbose=True, max_iterations=10)

    agent.update_prompts({"agent_worker:system_prompt": react_system_prompt})

    agent.reset()

    if os.environ.get("ENABLE_PROMPT"):
        prompt_dict = agent.get_prompts()
        for k, v in prompt_dict.items():
            print(f"Prompt: {k}\n\nValue: {v.template}")
    return agent
