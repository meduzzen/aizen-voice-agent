from app.core.config.agent.tools import TOOLS_SALESBOT
from app.core.config.prompts import Prompts
from app.core.mixins import LogMixin
from app.schemas.config import SessionConfig, Tool
from app.services.base_bot import BaseBotService
from app.services.openai_realtime import OpenAIRealtimeService
from app.services.tool_service import ToolService
from app.services.transcription import TranscriptionService


class WebBotService(BaseBotService, LogMixin):
    def __init__(
        self,
        transcription_service: TranscriptionService,
        openai_service: OpenAIRealtimeService,
        tool_service: ToolService,
    ) -> None:
        super().__init__(transcription_service, openai_service, tool_service)

    async def initialize_config(self) -> None:
        session_config = SessionConfig(
            instructions=Prompts.SYSTEM_PROMPT,
            tools=[Tool(**tool) for tool in TOOLS_SALESBOT],
        )
        self.openai_service.update_session_config(session_config)
