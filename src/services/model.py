from typing import Dict, List, Optional, AsyncGenerator
from ..agents.base import BaseAgent
from ..agents.devrev.devrev import DevRevAgent
from ..domains.chat import ModelResponse, ModelsResponse, ChatMessage, ChatResponse
import asyncio

class ModelService:
    def __init__(self):
        self.agents : Dict[str, BaseAgent] = {
            "dev-rev" : DevRevAgent()
        }

    async def chat_completion(self, model_id: str, messages: List[ChatMessage], max_tokens: Optional[int] = 50, temperature: Optional[float] = 0.7) -> AsyncGenerator[ChatResponse, None]:
        agent = self.agents.get(model_id)
        if not agent:
            raise ValueError(f"Model {model_id} not found.")
        async for response_chunk in agent.chat_completion(messages, max_tokens, temperature):
            yield response_chunk

    def list_models(self) -> ModelsResponse:
        return ModelsResponse(object="list", data=[ModelResponse(id=model_id, object="model", created=0, owned_by="dev-rev") for model_id in self.agents.keys()])
    
    def get_model_info(self, model_id: str) -> dict:
        agent = self.agents.get(model_id)
        if not agent:
            raise ValueError(f"Model {model_id} not found.")
        return {
            "model_id": model_id,
            "description": f"Information about {model_id}",
            "status": "active"
        }
    
    def delete_model(self, model_id: str):
        raise NotImplementedError("Delete model not implemented")