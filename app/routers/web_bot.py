from fastapi import APIRouter, WebSocket
from fastapi.responses import HTMLResponse

from app.core.dependencies import WebBotServiceDep

router = APIRouter(prefix="/web-bot", tags=["Web Bot"])


@router.get("/", response_class=HTMLResponse)
async def call_interface():
    return HTMLResponse(open(r"C:\WORK MEDUZZEN\voice\app\test\test.html").read())


@router.websocket("/media-stream")
async def handle_media_stream(
    websocket: WebSocket,
    web_bot_service: WebBotServiceDep,
) -> None:
    await web_bot_service.handle_media_stream(ws=websocket)
