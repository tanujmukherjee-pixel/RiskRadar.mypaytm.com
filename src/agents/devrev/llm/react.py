from llama_index.core.agent import ReActAgent
from llama_index.core.tools import QueryEngineTool, FunctionTool, ToolMetadata
from llama_index.llms.openai import OpenAI
import os
from ..tools.druid import execute_query_pulse, fetch_all_segments, get_all_funnels, fetch_query, fetch_all_applicable_segments
from ..tools.mongo import execute_query_mongo
from llama_index.core import PromptTemplate
from ....utils.trim import trim_context
import llama_index.core
import uuid


# import logging
# import sys

# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
# logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
# llama_index.core.set_global_handler("simple")

from datetime import datetime


def get_current_date():
    """
    Returns the current date in YYYY-MM-DD format
    """
    return datetime.now().strftime("%Y-%m-%d")

def get_date_window(start_date=None, end_date=None):
    """
    Returns start and end dates for analysis window.
    If dates not provided, defaults to last 30 days up to current date.
    
    Args:
        start_date (str, optional): Start date in YYYY-MM-DD format
        end_date (str, optional): End date in YYYY-MM-DD format
        
    Returns:
        tuple: (start_date, end_date) strings in YYYY-MM-DD format
    """
    today = datetime.now()
    
    if end_date is None:
        end_date = today.strftime("%Y-%m-%d")
        
    if start_date is None:
        from datetime import timedelta
        start = today - timedelta(days=7)
        start_date = start.strftime("%Y-%m-%d")
        
    return start_date, end_date

react_system_header_str = """\
You are an AI-powered Funnel Analysis Agent designed to deliver automatic summaries and insights from funnel data. Your capabilities include answering complex business questions, summarizing data, and performing in-depth analyses to identify root causes and actionable insights.

## Approach
1. Always start with a Thought.

2. Always use get_current_date tool to get the current date and not use current date from your system.

3. Identify Relevant Period: If start date window is missing then set it to 1 month ago. If end date window is missing then set it to today or current date using tool get_date_window.

4. Funnel Identification: Identify the relevant funnel related to the user's inquiry, ensuring comprehensive coverage of the data landscape. Leverage the tool get_all_funnels to get the list of all funnels.

5. Segment Identification: Always determine and explore all relevant segments for the inquiry, regardless of whether detailed segment analysis was initially specified. Always fetch results for ios, android, web segments. Also include any other segment which may be relevant to the inquiry.

6. Query Execution: Formulate and execute queries for the identified funnel and segments, ensuring data relevance and precision. Always fetch ios, android segments. If getting empty response from druid or pulse then use mongo tool to get the data.

7. Summary: 

    - Header should be in the format: "Funnel Analysis for <Funnel Name> from <start_date> to <end_date>"
    - Always create a leadership-level summary that includes concrete actions to take
    - Always Show step wise funnels with conversion percentages for each step. Always show total conversion percentage at the end of the summary in the table.
    - Show insights basis changes/trends at each stage via using change in conversion percentage from previous step.
    - Always convert numbers to short numbers using thousands, Lakhs and Crores with relevant suffix e.g. k, L, Cr.
    - Always include percentage change in conversion at each stage along with the absolute value in the same cell.
    - Always mention the list of funnels, segments and  used in the analysis.
    - Whenever user asks for daily or weekly insights then group the data by day or week. Weekly data should alwyas show last week upto current date even if the full week is not complete.
    
8. Final Answer:

    - Provide a final answer in inline html format by choosing the appropriate chart using plotly to present all data present, and produce the HTML to display it. based on the data try to make the scale of the chart as readable as possible. include an ways to explain any changes or trends observed at each stage. Also include percentage change in conversion at each stage along with the absolute value in the same cell. Only include initial stage and transition stages.
    - Always include a sequence of bullet points that explain how you arrived at the answer. This can include aspects of the previous conversation history.


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

Observation: response


You should keep repeating the above format until you have enough information
to answer the question without using any more tools. At that point, you MUST respond
in the one of the following two formats:

Thought: I can answer without using any more tools.
Answer: [your answer here]


Thought: I cannot answer the question with the provided tools.
Answer: Sorry, I cannot answer your query.

Only respond with Answer if you have enough information to answer the question for rest of the conversation respond with Thought and Action.

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
        model=os.environ.get("LLM_MODEL"),
        api_key=os.environ.get("OPENAI_API_KEY"),
        api_base=os.environ.get("OPENAI_API_BASE")
    )

    react_system_prompt = PromptTemplate(react_system_header_str)

    # Set up the query engine tool
    # query_engine_tool = QueryEngineTool(query_engine=query_engine, metadata=ToolMetadata(name="Docs", description="Tool to perform any other queries"))

    druid_tool = FunctionTool.from_defaults(fn=execute_query_pulse)
    segments_tool = FunctionTool.from_defaults(fn=fetch_all_segments)
    funnels_tool = FunctionTool.from_defaults(fn=get_all_funnels)
    base_query_tool = FunctionTool.from_defaults(fn=fetch_query)
    applicable_segments_tool = FunctionTool.from_defaults(fn=fetch_all_applicable_segments)
    # date_window_tool = FunctionTool.from_defaults(fn=get_date_window)
    mongo_tool = FunctionTool.from_defaults(fn=execute_query_mongo)
    current_date_tool = FunctionTool.from_defaults(fn=get_current_date)
    # trim_tool = FunctionTool.from_defaults(fn=trim_context)

    # Create the ReAct agent
    agent = ReActAgent.from_tools([druid_tool, segments_tool, funnels_tool, base_query_tool, applicable_segments_tool, mongo_tool, current_date_tool], llm=llm, verbose=True, max_iterations=50)

    agent.update_prompts({"agent_worker:system_prompt": react_system_prompt})

    agent.reset()

    if os.environ.get("ENABLE_PROMPT"):
        prompt_dict = agent.get_prompts()
        for k, v in prompt_dict.items():
            print(f"Prompt: {k}\n\nValue: {v.template}")
    return agent
