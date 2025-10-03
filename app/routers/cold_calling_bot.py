from fastapi import APIRouter, Request, WebSocket, status
from fastapi.responses import HTMLResponse

from app.core.config.enums import Methods
from app.core.dependencies import ColdCallingBotServiceDep, TwilioServiceDep
from app.schemas.twilio import OutgoingParamsSchema

router = APIRouter(prefix="/cold-calling", tags=["Cold Calling"])


@router.post("/make-call", response_model=OutgoingParamsSchema, status_code=status.HTTP_200_OK)
async def make_call(request: Request, twilio_service: TwilioServiceDep) -> OutgoingParamsSchema:
    return await twilio_service.make_call(request=request)


@router.api_route("/outgoing-call", methods=[Methods.GET, Methods.POST])
async def outgoing_call(request: Request, twilio_service: TwilioServiceDep) -> HTMLResponse:
    return await twilio_service.handle_outgoing_call(request=request)


@router.get("/", response_class=HTMLResponse)
async def call_interface():
    return HTMLResponse(open(r"C:\WORK MEDUZZEN\voice\app\test\test2.html").read())


@router.websocket("/media-stream")
async def handle_media_stream(websocket: WebSocket, cold_calling_bot_service: ColdCallingBotServiceDep) -> None:
    await cold_calling_bot_service.handle_media_stream(ws=websocket)
