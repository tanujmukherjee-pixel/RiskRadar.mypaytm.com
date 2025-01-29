from ..base import BaseAgent
from typing import List, Optional
from ...domains.chat import ChatMessage, ChatResponse
from .llm.react import react_query_engine

class DevRevAgent(BaseAgent):
    def __init__(self):
        super().__init__()

    def chat_completion(self, messages: List[ChatMessage], max_tokens: Optional[int] = 50, temperature: Optional[float] = 0.7) -> ChatResponse:
        agent = self.get_agent()
        message = ""
        for msg in messages:
            message += f"{msg.role}: {msg.content}\n"
        response = str(agent.chat(message))
        return ChatResponse(model="dev-rev", choices=[{"message": {"role": "assistant", "content": response}}])

    def get_agent(self):
        return react_query_engine()
