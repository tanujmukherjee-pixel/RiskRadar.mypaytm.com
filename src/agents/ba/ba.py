from ..base import BaseAgent

class BaAgent(BaseAgent):
    def __init__(self):
        super().__init__("ba",["current_date_tool", "execute_query_tool", "fetch_permitted_tables_tool", "fetch_permitted_schemas_tool"])