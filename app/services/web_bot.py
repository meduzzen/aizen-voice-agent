from langchain_openai import ChatOpenAI
from app.core.config.agent.tools import TOOLS_SALESBOT
from app.core.config.config import settings
from app.core.config.prompts import Prompts
from app.core.mixins import LogMixin
from app.schemas.config import InitMessages, SessionConfig, Tool
from app.services.base_bot import BaseBotService
from app.services.gohighlevel import GoHighLevelClient
from app.services.openai_realtime import OpenAIRealtimeService
from app.services.summary import SummaryService
from app.services.tool_service import ToolService
from app.services.transcription import TranscriptionService
from app.core.config.conversational_states import CONVERSATIONAL_STATES_WEBSALES_BOT
from app.services.twilio_service import TwilioService
from app.schemas.init_message import InitMessageSchema

class WebBotService(BaseBotService, LogMixin):
    def __init__(
        self,
        summary_service: SummaryService,
        transcription_service: TranscriptionService,
        openai_service: OpenAIRealtimeService,
        tool_service: ToolService,
        twilio_service: TwilioService,
        gohighlevel_service: GoHighLevelClient
    
    ) -> None:
        super().__init__(summary_service, transcription_service, openai_service, tool_service, twilio_service, gohighlevel_service)
        self.llm = ChatOpenAI(
            model=settings.open_ai.CHAT_MODEL,
            temperature=settings.open_ai.TEMPERATURE,
            api_key=settings.open_ai.OPENAI_API_KEY,
        )
        self.structured_llm = self.llm.with_structured_output(InitMessageSchema)

    async def initialize_config(self) -> None:
        session_config = SessionConfig(
            instructions=Prompts.SYSTEM_PROMPT.format(conversational_states=CONVERSATIONAL_STATES_WEBSALES_BOT, scenario=""),
            tools=[Tool(**tool) for tool in TOOLS_SALESBOT],
        )
        self.openai_service.update_session_config(session_config)
        
    async def choose_init_message(self) -> str:
        response = await self.structured_llm.ainvoke(Prompts.INIT_MESSAGE_SELECTOR_PROMPT,)
        chosen = response.message
        self.log(f"Chosen init message: {chosen}")
        return chosen
        
    async def initialize_init_messages(self):
        chosen_message = await self.choose_init_message()

        messages = [{"text": chosen_message}]

        self.log(f"Final INIT message to send: {chosen_message}")
        self.openai_service.update_init_messages(InitMessages(messages=messages))

