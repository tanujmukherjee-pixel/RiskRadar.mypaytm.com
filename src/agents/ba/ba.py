from ..base import BaseAgent

class BaAgent(BaseAgent):
    def __init__(self):
        if ENABLE_ALL_ACCESS:
            super().__init__("ba",["current_date_tool", "execute_query_tool", "fetch_all_datasets_tool", "fetch_schema_name_from_dataset_id_tool"])
        else:
            super().__init__("ba",["current_date_tool", "execute_query_tool", "fetch_permitted_tables_tool", "fetch_permitted_schemas_tool"])