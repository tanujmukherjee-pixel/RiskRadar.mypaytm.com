from fastapi import APIRouter, HTTPException, Depends, Request, UploadFile, File
from typing import Dict, Tuple, List
from ..services.tools import tools_service
from ..utils.python import parse_tool_file

router = APIRouter()

@router.get("/v1/tools", tags=["tools"])
async def list_tools():
    try:
        tools = tools_service.get_all_tools()
        return list(tools.keys())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/v1/tools", tags=["tools"])
async def create_tool(tool_file: UploadFile = File(...)):
    try:
        tools, imports = _validate_tool_file(tool_file)
        tools_service.save_tool(tools, imports)
        return {"message": "Tools created successfully", "tools": list(tools.keys())}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _validate_tool_file(tool_file: UploadFile) -> Tuple[Dict[str, str], List[str]]:
    file_content = tool_file.file.read().decode("utf-8")
    if not file_content:
        raise HTTPException(status_code=400, detail="Tool file is empty")

    return parse_tool_file(file_content)

@router.put("/v1/tools/{tool_name}", tags=["tools"])
async def update_tool(tool_name: str, tool_file: UploadFile = File(...)):
    try:
        tools, imports = _validate_tool_file(tool_file)
        tools_service.save_tool(tools, imports)
        return {"message": "Tool updated successfully", "tools": list(tools.keys())}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/v1/tools/{tool_name}", tags=["tools"])
async def delete_tool(tool_name: str):
    try:
        tools_service.delete_tool(tool_name)
        return {"message": "Tool deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))