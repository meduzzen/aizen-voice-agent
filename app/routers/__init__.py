from fastapi import APIRouter

from app.routers.cold_calling_bot import router as cold_calling_bot_router
from app.routers.knowledge_base import router as knowledge_base_router
from app.routers.web_bot import router as web_bot_router
from app.routers.chat_bot import router as chat_bot_router

__all__ = ["router"]

router = APIRouter()

router.include_router(knowledge_base_router)
router.include_router(web_bot_router)
router.include_router(cold_calling_bot_router)
router.include_router(chat_bot_router)
