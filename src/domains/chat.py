from pydantic import BaseModel
from typing import Optional, List

class ModelResponse(BaseModel):
    id: str
    object: str
    created: int
    owned_by: str

class ModelsResponse(BaseModel):
    object: str
    data: List[ModelResponse]
    
class ModelRequest(BaseModel):
    prompt: str
    max_tokens: Optional[int] = 50
    temperature: Optional[float] = 0.7

class ChatMessage(BaseModel):
    role: str  # e.g., 'user' or 'assistant'
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    max_tokens: Optional[int] = 50
    temperature: Optional[float] = 0.7

class ChatResponse(BaseModel):
    model: str
    choices: List[dict]
