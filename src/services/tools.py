from typing import Dict
from llama_index.core.tools import FunctionTool

class Tools:
    def __init__(self):
        self.tools : Dict[str, FunctionTool] = {}

    def add_tool(self, tool):
        self.tools.append(tool)

    def get_tool(self, tool_name: str) -> FunctionTool:
        return self.tools[tool_name]

    def get_all_tools(self) -> Dict[str, FunctionTool]:
        return self.tools
