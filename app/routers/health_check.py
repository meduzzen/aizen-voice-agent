from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(tags=["Health Check"], prefix="/health-check")


@router.get("", description="Check if server works")
async def healthcheck() -> JSONResponse:
    return JSONResponse(content="Server works")
