from ..base import BaseAgent

class FunnelAgent(BaseAgent):
    def __init__(self):
        super().__init__("funnel",["druid_tool", "segments_tool", "funnels_tool", "base_query_tool", "applicable_segments_tool", "mongo_tool", "current_date_tool"])