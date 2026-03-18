from llama_index.core.tools import FunctionTool

from ...tools.druid import (
    execute_query_pulse,
    fetch_all_applicable_segments,
    fetch_all_segments,
    fetch_query,
    get_all_funnels,
)
from ...tools.mongo import execute_query_mongo
from ...utils.time import get_current_date
from ..base import BaseAgent


class FunnelAgent(BaseAgent):
    def __init__(self):
        super().__init__("funnel", [])
        self.tools = self.get_tools()

    def get_tools(self):
        # Set up the query engine tool
        # query_engine_tool = QueryEngineTool(query_engine=query_engine, metadata=ToolMetadata(name="Docs", description="Tool to perform any other queries"))

        druid_tool = FunctionTool.from_defaults(fn=execute_query_pulse)
        segments_tool = FunctionTool.from_defaults(fn=fetch_all_segments)
        funnels_tool = FunctionTool.from_defaults(fn=get_all_funnels)
        base_query_tool = FunctionTool.from_defaults(fn=fetch_query)
        applicable_segments_tool = FunctionTool.from_defaults(
            fn=fetch_all_applicable_segments
        )
        mongo_tool = FunctionTool.from_defaults(fn=execute_query_mongo)
        current_date_tool = FunctionTool.from_defaults(fn=get_current_date)

        return [
            druid_tool,
            segments_tool,
            funnels_tool,
            base_query_tool,
            applicable_segments_tool,
            mongo_tool,
            current_date_tool,
        ]
