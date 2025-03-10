from typing import Dict, List, Optional, AsyncGenerator, Any
from ..agents.base import BaseAgent
from ..agents.funnel.funnel import FunnelAgent
from ..agents.ba.ba import BaAgent
from ..agents.bitbucket.bitbucket import BitbucketAgent
from ..domains.chat import ModelResponse, ModelsResponse, ChatMessage, ChatResponse
from ..rags.base import BaseRAG

class ModelService:
    def __init__(self):
        self.models : Dict[str, Any] = {
            "funnel" : FunnelAgent(),
            "ba" : BaAgent(),
            "bitbucket" : BitbucketAgent(),
            "neo4j" : BaseRAG("neo4j")
        }

    async def chat_completion(self, model_id: str, messages: List[ChatMessage], max_tokens: Optional[int] = 50, temperature: Optional[float] = 0.7) -> AsyncGenerator[ChatResponse, None]:
        model = self.models.get(model_id)
        if not model:
            raise ValueError(f"Model {model_id} not found.")
        async for response_chunk in model.chat_completion(messages, max_tokens, temperature):
            yield response_chunk

    def list_models(self) -> ModelsResponse:
        return ModelsResponse(object="list", data=[ModelResponse(id=model_id, object="model", created=0, owned_by="system") for model_id in self.models.keys()])
    
    def get_model_info(self, model_id: str) -> dict:
        model = self.models.get(model_id)
        if not model:
            raise ValueError(f"Model {model_id} not found.")
        return {
            "model_id": model_id,
            "description": f"Information about {model_id}",
            "status": "active"
        }
    
    def delete_model(self, model_id: str):
        try:
            self.models.pop(model_id)
        except KeyError:
            print(f"Model {model_id} not found.")
    
    def add_model(self, model_id: str, model: BaseAgent):
        self.models[model_id] = model

model_service = ModelService()