from ..base import BaseAgent

class RcLookupAgent(BaseAgent):
    def __init__(self):
        super().__init__("rc-lookup",["fetch_logs_tool","fetch_all_logs_tool","current_date_tool","fetch_rule_info_tool"])