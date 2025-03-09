from ..base import BaseAgent
from llama_index.core.tools import FunctionTool
from ...tools.druid import execute_query_pulse, fetch_all_segments, get_all_funnels, fetch_query, fetch_all_applicable_segments
from ...tools.mongo import execute_query_mongo
from ...utils.time import get_current_date

class FunnelAgent(BaseAgent):
    def __init__(self):
        super().__init__("funnel",["druid_tool", "segments_tool", "funnels_tool", "base_query_tool", "applicable_segments_tool", "mongo_tool", "current_date_tool"])