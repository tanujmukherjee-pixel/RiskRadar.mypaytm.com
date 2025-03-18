from ..base import BaseAgent

class BaAgent(BaseAgent):
    def __init__(self):
        super().__init__("ba",["fetch_all_datasets_tool", "fetch_dataset_schema_tool", "current_date_tool", "execute_query_tool"])