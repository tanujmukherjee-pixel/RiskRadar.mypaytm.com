from pydantic import BaseModel
from typing import Optional, List, Dict

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

class ChatMessage(BaseModel):
    role: str
    content: str

class BackgroundTasks(BaseModel):
    title_generation: bool
    tags_generation: bool

class Features(BaseModel):
    web_search: bool

class ChatCompletionRequest(BaseModel):
    stream: bool
    model: str
    messages: List[ChatMessage]

class Message(BaseModel):
    role: str
    content: Optional[str] = None
    reasoning_content: Optional[str] = None

class Choice(BaseModel):
    index: int
    message: Message
    finish_reason: Optional[str] = None

class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class ChatResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: List[Choice]
    usage: Optional[Usage] = None