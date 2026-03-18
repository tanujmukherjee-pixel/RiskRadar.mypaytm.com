from typing import AsyncGenerator, Dict, List, Optional

from ..agents.ba.ba import BaAgent
from ..agents.base import BaseAgent
from ..agents.bitbucket.bitbucket import BitbucketAgent
from ..agents.funnel.funnel import FunnelAgent
from ..domains.chat import ChatMessage, ChatResponse, ModelResponse, ModelsResponse


class ModelService:
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {
            "funnel": FunnelAgent(),
            "ba": BaAgent(),
            "bitbucket": BitbucketAgent(),
        }

    async def chat_completion(
        self,
        model_id: str,
        messages: List[ChatMessage],
        max_tokens: Optional[int] = 50,
        temperature: Optional[float] = 0.7,
    ) -> AsyncGenerator[ChatResponse, None]:
        agent = self.agents.get(model_id)
        if not agent:
            raise ValueError(f"Model {model_id} not found.")
        async for response_chunk in agent.chat_completion(
            messages, max_tokens, temperature
        ):
            yield response_chunk

    def list_models(self) -> ModelsResponse:
        return ModelsResponse(
            object="list",
            data=[
                ModelResponse(
                    id=model_id, object="model", created=0, owned_by="dev-rev"
                )
                for model_id in self.agents.keys()
            ],
        )

    def get_model_info(self, model_id: str) -> dict:
        agent = self.agents.get(model_id)
        if not agent:
            raise ValueError(f"Model {model_id} not found.")
        return {
            "model_id": model_id,
            "description": f"Information about {model_id}",
            "status": "active",
        }

    def complete_text(
        self,
        prompt: str,
        max_tokens: Optional[int] = 50,
        temperature: Optional[float] = 0.7,
    ) -> str:
        raise NotImplementedError("complete_text not implemented")

    def delete_model(self, model_id: str):
        raise NotImplementedError("Delete model not implemented")
