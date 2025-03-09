from ..base import BaseAgent
from llama_index.core.tools import FunctionTool
from ...utils.time import get_current_date
from ...tools.cdp import fetch_all_datasets, fetch_dataset_schema
from ...tools.starburst import execute_query, fetch_permitted_schemas, fetch_permitted_tables

class BaAgent(BaseAgent):
    def __init__(self):
        super().__init__("ba",["fetch_all_datasets_tool", "fetch_dataset_schema_tool", "current_date_tool", "execute_query_tool"])