from typing import Callable

from langchain_openai import ChatOpenAI

from app.core import settings
from app.core.mixins import LogMixin
from app.services.knowledge_base import KnowledgeBaseService
from app.services.twilio_service import TwilioService


class ToolService(LogMixin):
    def __init__(
        self,
        twilio_service: TwilioService,
        knowledge_base_service: KnowledgeBaseService,
        enabled_tools: list[str] | None = None,
    ) -> None:
        self.llm = ChatOpenAI(api_key=settings.open_ai.OPENAI_API_KEY, model=settings.open_ai.CHAT_MODEL)
        self.twilio_service = twilio_service
        self.knowledge_base_service = knowledge_base_service
        self.enabled_tools = enabled_tools or [
            "get_service_details",
            "finish_the_call",
            "redirect_to_manager",
        ]

    @property
    def tool_mapping(self) -> dict[str, Callable]:
        mapping = {
            "get_service_details": self.get_service_details,
            "finish_the_call": self.finish_the_call,
            "redirect_to_manager": self.redirect_to_manager,
        }
        return {k: v for k, v in mapping.items() if k in self.enabled_tools}

    async def get_service_details(self, query: str, *args, **kwargs) -> str:
        return await self.knowledge_base_service.retrieve(query)

    async def finish_the_call(self, call_sid: str, *args, **kwargs) -> None:
        return await self.twilio_service.handle_end_call(call_sid=call_sid)

    async def redirect_to_manager(self, call_sid: str, *args, **kwargs) -> None:
        return await self.twilio_service.redirect_to_manager(call_sid=call_sid)
