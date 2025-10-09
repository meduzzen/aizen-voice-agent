from langchain_openai import ChatOpenAI

from app.core.config.agent.tools import TOOLS_SALESBOT
from app.core.config.config import settings
from app.core.config.prompts import Prompts
from app.core.config.scenarios import SCENARIOS
from app.core.mixins import LogMixin
from app.mock.mocked_user import mocked_user
from app.schemas.client import GetClientSchema
from app.schemas.config import InitMessage, InitMessages, SessionConfig, Tool
from app.schemas.scenarios import ScenarioSchema
from app.services.base_bot import BaseBotService

# from app.services.elevenlabs import ElevenLabsService
from app.services.gohighlevel.client import GoHighLevelClient
from app.services.openai_realtime import OpenAIRealtimeService
from app.services.summary import SummaryService
from app.services.tool_service import ToolService
from app.services.transcription import TranscriptionService
from app.services.twilio_service import TwilioService


class ColdCallingBotService(BaseBotService, LogMixin):
    def __init__(
        self,
        summary_service: SummaryService,
        transcription_service: TranscriptionService,
        openai_service: OpenAIRealtimeService,
        tool_service: ToolService,
        twilio_service: TwilioService,
        gohighlevel_service: GoHighLevelClient
        # elevenlabs_service: ElevenLabsService
    ) -> None:
        super().__init__(summary_service=summary_service, transcription_service=transcription_service, openai_service=openai_service, tool_service=tool_service, twilio_service=twilio_service, gohighlevel_service=gohighlevel_service)
        self.llm = ChatOpenAI(
            model=settings.open_ai.CHAT_MODEL,
            temperature=settings.open_ai.TEMPERATURE,
            api_key=settings.open_ai.OPENAI_API_KEY,
        )
        self.structured_llm = self.llm.with_structured_output(ScenarioSchema)
        self.call_sid = None

        # self.previous_sentence = ""
        # self.elevenlabs_service = elevenlabs_service #TODO: uncomment if need to turn on ElevenLabs TTS
        self.twilio_service = twilio_service

    async def choose_scenario(self, crm_data: GetClientSchema) -> str:
        prompt = Prompts.SCENARIO_SELECTION_PROMPT.format(
            full_name=crm_data.full_name,
            company_name=crm_data.company_name,
            company_description=crm_data.company_description,
        )

        result = await self.structured_llm.ainvoke(prompt)
        scenario_name = result.scenario_name
        self.log(f"[COLD_CALLING_BOT] The chosen scenario: {scenario_name}")
        chosen_scenario = SCENARIOS[scenario_name]
        return chosen_scenario


    async def initialize_config(self, crm_data: dict = None) -> None:
        if crm_data is None:
            crm_data = GetClientSchema(**mocked_user)

        scenario = await self.choose_scenario(crm_data)

        session_config = SessionConfig(
            instructions=Prompts.SYSTEM_PROMPT.format(chosen_message="", chosen_question="", conversational_states="",scenario=scenario),
            tools=[Tool(**tool) for tool in TOOLS_SALESBOT],
        )

        self.openai_service.update_session_config(session_config)

    async def initialize_init_messages(self, crm_data: GetClientSchema = None) -> None:
        if crm_data is None:
            crm_data = GetClientSchema(**mocked_user)

        messages = [{"text": Prompts.COLD_BOT_INIT_MASSAGE.format(full_name=crm_data.full_name)}]
        messages = InitMessages(messages=[InitMessage(**message) for message in messages])

        self.openai_service.update_init_messages(messages)

    def parsing_start_data(self, start_data: dict) -> None:  # TODO: create a schema for the start_data and use it instead of dict
        self.stream_sid = start_data.get("streamSid")
        self.call_sid = start_data.get("callSid")
        self.log(f"[TWILIO] Stream START. streamSid={self.stream_sid} callSid={self.call_sid}")

    # async def proceed_sending_media(self, response: dict, ws: WebSocket, text: str) -> None: #TODO: uncomment if need to turn on ElevenLabs TTS
    # await self.elevenlabs_service.streaming(
    #     text=text, stream_sid=self.stream_sid, ws=ws, previous_message=self.previous_sentence
    # )
    # self.previous_sentence = text

    # async def _send_to_websocket(self, openai_ws: websockets.ClientConnection, ws: WebSocket) -> None:
    #     try:
    #         async for openai_message in openai_ws:
    #             response = json.loads(openai_message)
    #             event_type = response.get("type")
    #
    #             if event_type == OpenAIEvents.ASSISTANT_TRANSCRIPT:
    #                  async for chunk in self.transcription_service.proceed_llm_transcription(response=response):
    #                    await self.proceed_sending_media(response=response, ws=ws, text=chunk)
    #                    self.transcription_service.save_message_to_summary(speaker=Speaker.ASSISTANT, sentence=chunk, session_id=self.session_id)

    #             if event_type == OpenAIEvents.AUDIO_DELTA and "delta" in response:
    #                 await self.proceed_sending_media(response=response, ws=ws, text=response["delta"])

    #             if event_type == OpenAIEvents.CLIENT_TRANSCRIPT:
    #                 await self.transcription_service.proceed_user_transcription(
    #                     response=response, session_id=self.session_id
    #                 )

    #             if event_type == OpenAIEvents.SPEECH_STARTED:
    #                 await self.proceed_user_interruption(openai_ws=openai_ws, ws=ws)

    #             if event_type == OpenAIEvents.TOOL_CALL:
    #                 await self.execute_tool(data=response, openai_ws=openai_ws)

    #     except (websockets.ConnectionClosedOK, websockets.ConnectionClosedError) as e:
    #         self.log(f"[OPENAI_WS] recv closed: code={getattr(e, 'code', None)} reason={getattr(e, 'reason', None)}")
    #     except Exception as e:
    #         self.log(f"Error in send_to_twilio: {e}")
