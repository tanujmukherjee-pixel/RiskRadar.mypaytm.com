from ..base import BaseAgent
from llama_index.core.tools import FunctionTool
from ...utils.time import get_current_date
from ...tools.cdp import fetch_all_relevant_tables, fetch_table_schema
from ...tools.starburst import execute_query

class BaAgent(BaseAgent):
    def __init__(self):
        super().__init__("ba",[])
        self.tools = self.get_tools()
    
    def get_tools(self):
        # Set up the query engine tool
        # query_engine_tool = QueryEngineTool(query_engine=query_engine, metadata=ToolMetadata(name="Docs", description="Tool to perform any other queries"))
        fetch_relevant_tables_tool = FunctionTool.from_defaults(fn=fetch_all_relevant_tables)
        current_date_tool = FunctionTool.from_defaults(fn=get_current_date)
        fetch_table_schema_tool = FunctionTool.from_defaults(fn=fetch_table_schema)
        execute_query_tool = FunctionTool.from_defaults(fn=execute_query)
        return [fetch_relevant_tables_tool, current_date_tool, fetch_table_schema_tool, execute_query_tool]