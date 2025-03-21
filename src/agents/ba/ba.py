from ..base import BaseAgent

class BaAgent(BaseAgent):
    def __init__(self):
        super().__init__("ba",["fetch_all_datasets_tool", "fetch_schema_name_from_dataset_id_tool", "current_date_tool", "execute_query_tool"])