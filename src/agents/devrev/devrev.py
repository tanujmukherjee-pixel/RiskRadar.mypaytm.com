from ..base import BaseAgent
from typing import List, Optional
from ...domains.chat import ChatMessage, ChatResponse, Choice, Message, Usage
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
        return ChatResponse(
            id="unique-id",
            object="chat.completion",
            created=1234567890,
            model="dev-rev",
            choices=[
                Choice(
                    index=0,
                    message=Message(role="assistant", content=response),
                    finish_reason="stop"
                )
            ],
            usage=Usage(prompt_tokens=10, completion_tokens=20, total_tokens=30),
        )

    def get_agent(self):
        return react_query_engine()
