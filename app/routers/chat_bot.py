from fastapi import APIRouter, WebSocket

from app.core.dependencies.chat import ChatBotServiceDep


router = APIRouter(prefix="/chat-bot", tags=["Chat"])


@router.websocket("/chat")
async def chat_ws(ws: WebSocket, svc: ChatBotServiceDep):
    await svc.handle_ws(ws)
