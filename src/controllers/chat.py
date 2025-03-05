from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List, Optional, Dict, AsyncGenerator
from fastapi.responses import StreamingResponse
from ..services.model import ModelService
from ..domains.chat import ModelRequest, ChatCompletionRequest, ChatResponse
import json
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

@router.post("/v1/chat/completions", tags=["chat"])
async def chat_completion(request: ChatCompletionRequest, fastapi_request: Request):
    # Log the Accept header
    accept_header = fastapi_request.headers.get('accept')
    print(f"Accept header: {accept_header}")

    async def event_generator():
        try:
            async for chunk in model_service.chat_completion(
                model_id=request.model, 
                messages=request.messages
            ):
                # Directly yield the JSON object as bytes
                yield f"data: {json.dumps(chunk.model_dump())}\n\n".encode('utf-8')  # Format as SSE data
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail=str(e))

    if request.stream:
        return StreamingResponse(
            event_generator(),
            media_type='text/event-stream'
        )
    else:
        # Collect all chunks into a single response
        response = ""
        async for chunk in event_generator():
            response = chunk
        return response

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