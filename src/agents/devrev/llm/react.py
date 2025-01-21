from llama_index.core.agent import ReActAgent
from llama_index.core.tools import QueryEngineTool, FunctionTool, ToolMetadata
from llama_index.llms.azure_openai import AzureOpenAI
import os
from .query import query_engine

def react_query_engine():
    """
    Creates and returns a ReAct agent that utilizes both the query engine and Kibana logs fetcher.
    """
    llm = AzureOpenAI(
        model="gpt-35-turbo-16k",
        deployment_name="rc-lookup-gpt4",
        api_key="78323645757b409fa5ea920e66476eb4",
        azure_endpoint="https://rc-lookup-aust-east.openai.azure.com/",
        api_version="2023-07-01-preview",
    )

    # Set up the query engine tool
    query_engine_tool = QueryEngineTool(query_engine=query_engine, metadata=ToolMetadata(name="Docs", description="Provides all metadata"))

    # Create the ReAct agent
    agent = ReActAgent.from_tools([query_engine_tool], llm=llm, verbose=True, max_iterations=20)

    if os.environ.get("ENABLE_PROMPT"):
        prompt_dict = agent.get_prompts()
        for k, v in prompt_dict.items():
            print(f"Prompt: {k}\n\nValue: {v.template}")
    return agent
