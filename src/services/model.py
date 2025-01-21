from typing import Dict, List, Optional
from ..agents.base import BaseAgent
from ..agents.devrev.devrev import DevRevAgent
from ..domains.chat import ModelResponse, ModelsResponse, ChatMessage, ChatResponse

class ModelService:
    def __init__(self):
        self.agents : Dict[str, BaseAgent] = {
            "dev-rev" : DevRevAgent()
        }

    def chat_completion(self, model_id: str, messages: List[ChatMessage], max_tokens: Optional[int] = 50, temperature: Optional[float] = 0.7) -> ChatResponse:
        agent = self.agents.get(model_id)
        if not agent:
            raise ValueError(f"Model {model_id} not found.")
        return agent.chat_completion(messages, max_tokens, temperature)

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