from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse

from app.core.dependencies import KnowledgeBaseServiceDep

router = APIRouter(prefix="/knowledge_base", tags=["Knowledge Base"])


@router.post("/upload", description="Upload a file to Knowledge Base about services")
async def upload_file(knowledge_base_service: KnowledgeBaseServiceDep, file: UploadFile = File(...)) -> JSONResponse:
    await knowledge_base_service.load_to_memory(file)
    return JSONResponse(content="The document has been loaded successfully")
