from fastapi import APIRouter, File, UploadFile, Query
from fastapi.responses import JSONResponse

from app.core.dependencies import KnowledgeBaseServiceDep

router = APIRouter(prefix="/knowledge_base", tags=["Knowledge Base"])


@router.post("/upload", description="Upload a file to Knowledge Base about services")
async def upload_file(knowledge_base_service: KnowledgeBaseServiceDep, file: UploadFile = File(...),
                      flow: str = Query(None, description="logical flow metadata: candidate/client"),
                      collection: str = Query(..., description="kb_candidates or kb_clients")
                      ) -> JSONResponse:
    await knowledge_base_service.load_to_memory(file=file, collection_name=collection, flow=flow)
    return JSONResponse(content=f"Loaded into {collection}")
