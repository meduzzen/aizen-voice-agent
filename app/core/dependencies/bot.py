from typing import Annotated

from fastapi import Depends

from app.core.dependencies.services import OpenAIRealtimeDep, TwilioServiceDep, GHLServiceDep, SummaryServiceDep
from app.core.dependencies.tool import ToolServiceSalesDep, ToolServiceColdCallingDep
from app.core.dependencies.transcription import TranscriptionServiceDep
from app.services.cold_calling_bot import ColdCallingBotService
from app.services.web_bot import WebBotService



async def get_cold_calling_bot_service(
    summary_service: SummaryServiceDep,
    transcription_service: TranscriptionServiceDep,
    openai_service: OpenAIRealtimeDep,
    tool_service: ToolServiceColdCallingDep,
    twilio_service: TwilioServiceDep,
    gohighlevel_service: GHLServiceDep,
) -> ColdCallingBotService:
    return ColdCallingBotService(
        summary_service=summary_service,
        transcription_service=transcription_service,
        openai_service=openai_service,
        tool_service=tool_service,
        twilio_service=twilio_service,
        gohighlevel_service=gohighlevel_service,
    )


async def get_web_bot_service(
    summary_service: SummaryServiceDep,
    transcription_service: TranscriptionServiceDep,
    openai_service: OpenAIRealtimeDep,
    tool_service: ToolServiceSalesDep,
    twilio_service: TwilioServiceDep,
    gohighlevel_service: GHLServiceDep,
) -> WebBotService:
    return WebBotService(
        summary_service=summary_service,
        transcription_service=transcription_service,
        openai_service=openai_service,
        tool_service=tool_service,
        twilio_service=twilio_service,
        gohighlevel_service=gohighlevel_service,
    )


WebBotServiceDep = Annotated[WebBotService, Depends(get_web_bot_service)]
ColdCallingBotServiceDep = Annotated[ColdCallingBotService, Depends(get_cold_calling_bot_service)]
