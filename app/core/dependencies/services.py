from typing import Annotated

from fastapi import Depends

from app.services.elevenlabs import ElevenLabsService
from app.services.gohighlevel.appointment import Appointment
from app.services.gohighlevel.calendar import Calendar
from app.services.gohighlevel.client import GoHighLevelClient
from app.services.gohighlevel.contact import Contact
from app.services.knowledge_base import KnowledgeBaseService
from app.services.openai_realtime import OpenAIRealtimeService
from app.services.summary import SummaryService
from app.services.twilio_service import TwilioService

KnowledgeBaseServiceDep = Annotated[KnowledgeBaseService, Depends(KnowledgeBaseService)]
TwilioServiceDep = Annotated[TwilioService, Depends(TwilioService)]
SummaryServiceDep = Annotated[SummaryService, Depends(SummaryService)]
ElevenLabsServiceDep = Annotated[ElevenLabsService, Depends(ElevenLabsService)]
OpenAIRealtimeDep = Annotated[OpenAIRealtimeService, Depends(OpenAIRealtimeService)]


async def get_gohighlevel_service(
    summary_service: SummaryServiceDep,
) -> GoHighLevelClient:
    return GoHighLevelClient(
        contact_service=Contact(),
        appointment_service=Appointment(),
        calendar_service=Calendar(),
        summary_service=summary_service,
    )


GHLServiceDep = Annotated[GoHighLevelClient, Depends(get_gohighlevel_service)]
