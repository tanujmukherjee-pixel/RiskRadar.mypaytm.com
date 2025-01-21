from fastapi import APIRouter, HTTPException
from typing import List, Optional
from ..services.model import ModelService
from ..domains.chat import ModelRequest, ChatCompletionRequest, ChatResponse

router = APIRouter()
model_service = ModelService()

@router.get("/api/models", tags=["models"])
async def list_models():
    """
    List all available models.
    """
    try:
        models = model_service.list_models()
        return {"models": models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/complete", response_model=dict, tags=["completions"])
async def complete_text(request: ModelRequest):
    """
    Generate a text completion for a given prompt.
    """
    try:
        response = model_service.complete_text(request.prompt, request.max_tokens, request.temperature)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/chat/completion", response_model=ChatResponse, tags=["chat"])
async def chat_completion(request: ChatCompletionRequest):
    """
    Generate a chat completion from a series of messages.
    """
    try:
        response = model_service.chat_completion(request.model, request.messages, request.max_tokens, request.temperature)
        return response
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/models/{model_id}", tags=["models"])
async def get_model_info(model_id: str):
    """
    Get information about a specific model.
    """
    try:
        model_info = model_service.get_model_info(model_id)
        return model_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/api/models/{model_id}/delete", tags=["models"])
async def delete_model(model_id: str):
    """
    Delete a specific model.
    """
    try:
        model_service.delete_model(model_id)
        return {"message": f"Model {model_id} deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))