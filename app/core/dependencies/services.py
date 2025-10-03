from typing import Annotated

from fastapi import Depends

from app.services.elevenlabs import ElevenLabsService
from app.services.knowledge_base import KnowledgeBaseService
from app.services.openai_realtime import OpenAIRealtimeService
from app.services.summary import SummaryService
from app.services.twilio_service import TwilioService

KnowledgeBaseServiceDep = Annotated[KnowledgeBaseService, Depends(KnowledgeBaseService)]
TwilioServiceDep = Annotated[TwilioService, Depends(TwilioService)]
SummaryServiceDep = Annotated[SummaryService, Depends(SummaryService)]
ElevenLabsServiceDep = Annotated[ElevenLabsService, Depends(ElevenLabsService)]
OpenAIRealtimeDep = Annotated[OpenAIRealtimeService, Depends(OpenAIRealtimeService)]
