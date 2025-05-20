from typing import List, Optional, Any
from ..domains.chat import ChatMessage
from pydantic import BaseModel

class StateAgent(BaseModel):
    agent: Any = None
    condition: Optional[str] = None

class State(BaseModel):
    current_agent: Any = None
    messages: List[ChatMessage] = []
    is_interrupted: bool = False
    is_done: bool = False       
    all_agents: List[StateAgent] = []