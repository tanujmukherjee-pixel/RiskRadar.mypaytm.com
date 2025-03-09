from typing import Dict
from llama_index.core.tools import FunctionTool
from ..tools import tools
from ..constants.path import TOOLS_PATH
from typing import List
from ..repositories.tool import tool_repository
from ..utils.file import write_file

class Tools:
    def __init__(self):
        self.tools : Dict[str, FunctionTool] = {}
        self._populate_tools()

    def bootstrap(self):
        print("Bootstrapping tools")
        tools = tool_repository.list_tools()
        for tool in tools:
            import os
            os.makedirs(os.path.dirname(TOOLS_PATH.format(tool_name=tool['name'])), exist_ok=True)
            write_file(TOOLS_PATH.format(tool_name=tool['name']), tool['file_content'])
            self._load_tool(tool['name'])
        print("Tools bootstrapped")

    def _populate_tools(self):
        for tool_name, tool in tools.items():
            self.tools[tool_name] = tool

    def add_tool(self, tool):
        self.tools.append(tool)

    def get_tool(self, tool_name: str) -> FunctionTool:
        return self.tools[tool_name]

    def get_all_tools(self) -> Dict[str, FunctionTool]:
        return self.tools

    def save_tool(self, tools: Dict[str, str], imports: List[str]) -> None:
        contents = self._save_tool_file(tools, imports)
        for tool_name, tool_content in contents.items():
            tool_data = {
                "name": tool_name,
                "description": tool_name,
                "file_content": contents[tool_name],
            }
            tool_repository.create_tool(tool_data)
            self._load_tool(tool_name)

    def _load_tool(self, tool_name: str) -> FunctionTool:
        # Import function from saved file path
        import importlib.util
        spec = importlib.util.spec_from_file_location(tool_name, TOOLS_PATH.format(tool_name=tool_name))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        function_tool = FunctionTool.from_defaults(fn=getattr(module, tool_name))
        self.tools[tool_name] = function_tool

    def _save_tool_file(self, tools: Dict[str, str], imports: List[str]) -> None:
        contents = {}
        for tool_name, tool_content in tools.items():
            import os
            os.makedirs(os.path.dirname(TOOLS_PATH.format(tool_name=tool_name)), exist_ok=True)
            tool_path = TOOLS_PATH.format(tool_name=tool_name)
            file_content = ""
            for import_statement in imports:
                file_content += import_statement + "\n"
            file_content += "\n"
            file_content += tool_content
            write_file(tool_path, file_content)
            contents[tool_name] = file_content
        return contents


tools_service = Tools()