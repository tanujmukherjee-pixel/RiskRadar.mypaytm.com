from typing import List, Optional
from ..domains.chat import ChatMessage, ChatResponse

class BaseAgent:
    def __init__(self):
        pass

    def chat_completion(self, messages: List[ChatMessage], max_tokens: Optional[int] = 50, temperature: Optional[float] = 0.7) -> ChatResponse:
        pass