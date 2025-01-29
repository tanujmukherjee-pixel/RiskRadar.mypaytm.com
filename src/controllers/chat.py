from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict
from ..services.model import ModelService
from ..domains.chat import ModelRequest, ChatCompletionRequest, ChatResponse

router = APIRouter()
model_service = ModelService()

@router.get("/v1/models", tags=["models"])
async def list_models():
    """
    List all available models.
    """
    try:
        models = model_service.list_models()
        return models  # OpenAI API typically returns a "data" field with models
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/v1/completions", response_model=dict, tags=["completions"])
async def create_completion(request: ModelRequest):
    """
    Generate a text completion for a given prompt.
    """
    try:
        response = model_service.complete_text(
            prompt=request.prompt, 
            max_tokens=request.max_tokens, 
            temperature=request.temperature
        )
        return {"choices": [{"text": response}]}  # Aligning with OpenAI's response format
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/v1/chat/completions", response_model=ChatResponse, tags=["chat"])
async def chat_completion(request: ChatCompletionRequest):
    try:
        # Example response handling
        response = model_service.chat_completion(
            model_id=request.model, 
            messages=request.messages
        )
        return response
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/v1/models/{model_id}", tags=["models"])
async def retrieve_model(model_id: str):
    """
    Get information about a specific model.
    """
    try:
        model_info = model_service.get_model_info(model_id)
        return model_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/v1/models/{model_id}", tags=["models"])
async def delete_model(model_id: str):
    """
    Delete a specific model.
    """
    try:
        model_service.delete_model(model_id)
        return {"message": f"Model {model_id} deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))