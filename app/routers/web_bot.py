from pathlib import Path
from fastapi import APIRouter, Request, WebSocket
from fastapi.responses import HTMLResponse
from app.core.config.config import settings
from app.core.config.enums import Methods
from app.core.dependencies import WebBotServiceDep
from app.core.dependencies.services import TwilioServiceDep
from app.schemas.twilio import OutgoingParamsSchema

router = APIRouter(prefix="/web-bot", tags=["Web Bot"])

@router.post("/make-call", response_model=OutgoingParamsSchema)
async def make_call(request: Request, twilio_service: TwilioServiceDep) -> OutgoingParamsSchema:
    return await twilio_service.make_call(request=request)


@router.api_route("/outgoing-call", methods=[Methods.GET, Methods.POST])
async def outgoing_call(request: Request, twilio_service: TwilioServiceDep) -> HTMLResponse:
    return await twilio_service.handle_outgoing_call(request=request)


@router.get("/", response_class=HTMLResponse)
async def call_interface():
    file_path = Path(__file__).parent.parent / "test" / "test.html"
    if not file_path.exists():
        return HTMLResponse(f"<h1>File not found: {file_path}</h1>", status_code=404)

    return HTMLResponse(file_path.read_text(encoding="utf-8"))

@router.websocket("/media-stream")
async def handle_media_stream(
    websocket: WebSocket,
    web_bot_service: WebBotServiceDep,
) -> None:
    await web_bot_service.handle_media_stream(ws=websocket)
