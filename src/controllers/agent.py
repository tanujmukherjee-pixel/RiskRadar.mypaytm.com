from fastapi import APIRouter, HTTPException, Depends, Request, UploadFile, File
from typing import Dict, Any
from ..services.agent import agent_service
from ..domain.agent_request import AgentRequest
import json
from ..constants.path import SYSTEM_PROMPT_FILE, APPROACH_PROMPT_FILE, OUTPUT_PROMPT_FILE

router = APIRouter()

@router.post("/v1/agents/", response_model=Dict, tags=["agents"])
async def create_agent(
    agent_request: str,
    file: UploadFile = File(...)
):
    if not file:
        raise HTTPException(status_code=400, detail="ZIP file is required.")
    
    agent_request = AgentRequest(**json.loads(agent_request))
    prompts = _validate_zip_file(file)
    agent = await agent_service.create_agent(agent_request, prompts)

    return {"message": f"Agent {agent.agent_name} created successfully"}


def _validate_zip_file(zip_file: UploadFile):
    if zip_file.content_type != "application/zip":
        raise HTTPException(status_code=400, detail="ZIP file is required.")
    import zipfile
    from io import BytesIO
    
    # Read zip file into memory
    zip_content = BytesIO(zip_file.file.read())
    
    # Check zip contents
    required_files = {SYSTEM_PROMPT_FILE, APPROACH_PROMPT_FILE, OUTPUT_PROMPT_FILE}
    with zipfile.ZipFile(zip_content) as zf:
        zip_files = set(zf.namelist())
        
        # Validate required files exist
        missing_files = required_files - zip_files
        if missing_files:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required files: {', '.join(missing_files)}"
            )
            
        # Validate no extra files
        extra_files = zip_files - required_files
        if extra_files:
            raise HTTPException(
                status_code=400,
                detail=f"Zip contains unexpected files: {', '.join(extra_files)}"
            )

    # Read contents of required files
    file_contents = {}
    with zipfile.ZipFile(zip_content) as zf:
        for filename in required_files:
            file_contents[filename] = zf.read(filename).decode('utf-8')
    
    return file_contents


@router.put("/v1/agents/{agent_name}", tags=["agents"])
async def update_agent(
    agent_name: str,
    agent_request: str,
    file: UploadFile = File(...)
):
    if not file:
        raise HTTPException(status_code=400, detail="ZIP file is required.")
    
    agent_request = AgentRequest(**json.loads(agent_request))
    prompts = _validate_zip_file(file)
    agent = await agent_service.create_agent(agent_request, prompts)
    return {"message": f"Agent {agent.agent_name} updated successfully"}


@router.delete("/v1/agents/{agent_name}", tags=["agents"])
async def delete_agent(agent_name: str):
    agent_service.delete_agent(agent_name)
    return {"message": f"Agent {agent_name} deleted successfully"}