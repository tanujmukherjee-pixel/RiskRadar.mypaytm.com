from ..base import BaseAgent

class RcLookupAgent(BaseAgent):
    def __init__(self):
        super().__init__("rc-lookup",["fetch_all_logs_tool","current_date_tool","fetch_rule_info_tool", "calculate_cooloff_period_tool", "fetch_logs_timerange_tool"])