from typing import Annotated

from fastapi import Depends

from app.core.dependencies.services import SummaryServiceDep
from app.services.transcription import TranscriptionService


async def get_transcription_service(
    summary_service: SummaryServiceDep,
) -> TranscriptionService:
    return TranscriptionService(summary_service=summary_service)


TranscriptionServiceDep = Annotated[TranscriptionService, Depends(get_transcription_service)]
