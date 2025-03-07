from ..base import BaseAgent
from llama_index.core.tools import FunctionTool
from ...utils.time import get_current_date
from ...tools.cdp import fetch_all_datasets, fetch_dataset_schema
from ...tools.starburst import execute_query, fetch_permitted_schemas, fetch_permitted_tables

class BaAgent(BaseAgent):
    def __init__(self):
        super().__init__("ba",[])
        self.tools = self.get_tools()
    
    def get_tools(self):
        # Set up the query engine tool
        # query_engine_tool = QueryEngineTool(query_engine=query_engine, metadata=ToolMetadata(name="Docs", description="Tool to perform any other queries"))
        fetch_all_datasets_tool = FunctionTool.from_defaults(fn=fetch_all_datasets)
        fetch_dataset_schema_tool = FunctionTool.from_defaults(fn=fetch_dataset_schema)
        current_date_tool = FunctionTool.from_defaults(fn=get_current_date)
        execute_query_tool = FunctionTool.from_defaults(fn=execute_query)
        # fetch_permitted_schemas_tool = FunctionTool.from_defaults(fn=fetch_permitted_schemas)
        # fetch_permitted_tables_tool = FunctionTool.from_defaults(fn=fetch_permitted_tables)
        return [fetch_all_datasets_tool, fetch_dataset_schema_tool, current_date_tool, execute_query_tool]