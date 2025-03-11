from typing import Dict, Any

class NoopAgentRepository:
    def __init__(self):
        pass

    def create_agent(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new agent record or update if exists"""
        return {}

    def get_agent(self, agent_id: int) -> Dict[str, Any]:
        return {}

    def update_agent(self, agent_id: int, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        return {}

    def delete_agent(self, agent_name: str) -> bool:
        return False

    def list_agents(self) -> list[Dict[str, Any]]:
        return []

    def list_agents_by_tool(self, tool_name: str) -> list[Dict[str, Any]]:
        return []

    def __del__(self):
        pass

def get_repository():
    return NoopAgentRepository()