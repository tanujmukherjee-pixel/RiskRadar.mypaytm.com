from pydantic import BaseModel
from typing import Optional

class AgentRequest(BaseModel):
    name: str
    list_of_tools: list
    description: Optional[str] = None

    def __init__(self, name: str, list_of_tools: list, description: Optional[str] = None):
        super().__init__(name=name, list_of_tools=list_of_tools, description=description)

    def __repr__(self):
        return f"AgentRequest(name={self.name}, list_of_tools={self.list_of_tools}, description={self.description})"