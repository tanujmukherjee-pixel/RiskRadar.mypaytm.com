from typing import Dict, Any

class NoopToolRepository:
    def __init__(self):
        pass

    def create_tool(self, tool_data: Dict[str, Any]) -> Dict[str, Any]:
        return {}

    def get_tool(self, tool_id: int) -> Dict[str, Any]:
        return {}

    def update_tool(self, tool_id: int, tool_data: Dict[str, Any]) -> Dict[str, Any]:
        return {}

    def delete_tool(self, tool_name: str) -> bool:
        return False

    def list_tools(self) -> list[Dict[str, Any]]:
        return []

    def __del__(self):
        pass

def get_repository():
    return NoopToolRepository()