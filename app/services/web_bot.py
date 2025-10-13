import random

from app.core.config.agent.tools import TOOLS_SALESBOT
from app.core.config.conversational_states import CONVERSATIONAL_STATES_WEBSALES_BOT
from app.core.config.init_messages import FOLLOW_UP_QUESTIONS_VARIATIONS, INIT_MESSAGES
from app.core.config.prompts import Prompts
from app.core.mixins import LogMixin
from app.schemas.config import InitMessages, SessionConfig, Tool
from app.services.base_bot import BaseBotService
from app.services.gohighlevel.client import GoHighLevelClient
from app.services.openai_realtime import OpenAIRealtimeService
from app.services.summary import SummaryService
from app.services.tool_service import ToolService
from app.services.transcription import TranscriptionService
from app.services.twilio_service import TwilioService


class WebBotService(BaseBotService, LogMixin):
    def __init__(
        self,
        summary_service: SummaryService,
        transcription_service: TranscriptionService,
        openai_service: OpenAIRealtimeService,
        tool_service: ToolService,
        twilio_service: TwilioService,
        gohighlevel_service: GoHighLevelClient,
    ) -> None:
        super().__init__(summary_service, transcription_service, openai_service, tool_service, twilio_service, gohighlevel_service)
        self.chosen_message = random.choice(INIT_MESSAGES)
        self.chosen_question = random.choice(FOLLOW_UP_QUESTIONS_VARIATIONS)

    async def initialize_config(self) -> None:
        self.log(f"Chosen init message: {self.chosen_message}")
        self.log(f"chosen question: {self.chosen_question}")
        session_config = SessionConfig(
            instructions=Prompts.SYSTEM_PROMPT.format(
                chosen_message=self.chosen_message,
                chosen_question=self.chosen_question,
                conversational_states=CONVERSATIONAL_STATES_WEBSALES_BOT,
                scenario="",
            ),
            tools=[Tool(**tool) for tool in TOOLS_SALESBOT],
        )
        self.openai_service.update_session_config(session_config)

    async def initialize_init_messages(self):
        messages = [{"text": self.chosen_message}]

        self.log(f"Final INIT message to send: {self.chosen_message}")
        self.openai_service.update_init_messages(InitMessages(messages=messages))
