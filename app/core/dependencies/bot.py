from typing import Annotated

from fastapi import Depends

from app.core.dependencies.services import OpenAIRealtimeDep, TwilioServiceDep
from app.core.dependencies.tool import ToolServiceDep
from app.core.dependencies.transcription import TranscriptionServiceDep
from app.services.cold_calling_bot import ColdCallingBotService
from app.services.web_bot import WebBotService


async def get_cold_calling_bot_service(
    transcription_service: TranscriptionServiceDep,
    openai_service: OpenAIRealtimeDep,
    tool_service: ToolServiceDep,
    twilio_service: TwilioServiceDep,
) -> ColdCallingBotService:
    return ColdCallingBotService(
        transcription_service=transcription_service,
        openai_service=openai_service,
        tool_service=tool_service,
        twilio_service=twilio_service,
    )


async def get_web_bot_service(
    transcription_service: TranscriptionServiceDep,
    openai_service: OpenAIRealtimeDep,
    tool_service: ToolServiceDep,
) -> WebBotService:
    return WebBotService(
        transcription_service=transcription_service,
        openai_service=openai_service,
        tool_service=tool_service,
    )


WebBotServiceDep = Annotated[WebBotService, Depends(get_web_bot_service)]
ColdCallingBotServiceDep = Annotated[ColdCallingBotService, Depends(get_cold_calling_bot_service)]
