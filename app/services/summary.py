from uuid import UUID

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI

from app.core import settings
from app.core.config.prompts import Prompts
from app.core.mixins import LogMixin
from app.schemas.messenger import PostSummaryOptions
from app.schemas.summary import MessageSchema, Speaker, SummarySchema


class SummaryService(LogMixin):
    def __init__(self):
        self.call_transcription: dict[UUID, list[MessageSchema]] = {}
        self.llm = self.get_llm()

    def get_full_transcript(self, session_id: UUID) -> list[MessageSchema]:
        return self.call_transcription.get(session_id, [])

    def add_message(self, session_id: UUID, message: str, speaker: Speaker) -> None:
        if session_id in self.call_transcription:
            self.call_transcription[session_id].append(MessageSchema(type=speaker, content=message))
        else:
            self.call_transcription[session_id] = [MessageSchema(type=speaker, content=message)]

    @staticmethod
    def get_llm():
        llm = ChatOpenAI(model=settings.open_ai.CHAT_MODEL, api_key=settings.open_ai.OPENAI_API_KEY)
        return llm.with_structured_output(SummarySchema)

    async def create_summary(self, session_id: UUID, phone_number: str | None = None) -> SummarySchema:
        summary_prompt = self.summary_prompt(session_id=session_id)
        result = await self.llm.ainvoke(summary_prompt)
        if phone_number:
            result.phone_number = phone_number
        return result

    def messages_from_dict(self, messages: list[MessageSchema]) -> list[BaseMessage]:
        """Transform dicts of messages into BaseMessage objects"""
        return [self.message_from_dict(message) for message in messages] if messages else []

    @staticmethod
    def message_from_dict(message_dict: MessageSchema) -> BaseMessage:
        """Transform a single-message dict into a BaseMessage object"""
        return HumanMessage(content=message_dict.content) if message_dict.type == "Client" else AIMessage(content=message_dict.content)

    def summary_prompt(self, session_id: UUID) -> list[BaseMessage]:
        summary_message = "Create a summary of the conversation above. " + Prompts.SUMMARIZATION_PROMPT

        formatted_messages = self.messages_from_dict(messages=self.call_transcription.get(session_id))

        return formatted_messages + [HumanMessage(content=summary_message)]

    async def send_summary(self, post_option: PostSummaryOptions, session_id: UUID, phone_number: str | None = None) -> None:
        try:
            tag = post_option.value.upper()

            summary = await self.create_summary(
                session_id=session_id,
                phone_number=phone_number,
            )
            self.log(f"[{tag}][DEBUG] summary='{summary}'")

            # integration = IntegrationRegistry.get(post_option)
            # await integration.send_summary(summary)
        except Exception as e:
            self.log(f"[SUMMARY][ERROR] {e}")
