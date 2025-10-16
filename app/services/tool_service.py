import asyncio
import re
from typing import Callable

from langchain_openai import ChatOpenAI

from app.core import settings
from app.core.config.enums import GoHighLevel
from app.core.mixins import LogMixin
from app.schemas.gohighlevel.contact import ContactDetail, CustomFieldSchema
from app.services.gohighlevel.client import GoHighLevelClient
from app.services.knowledge_base import KnowledgeBaseService
from app.services.twilio_service import TwilioService


class ToolService(LogMixin):
    def __init__(
        self,
        twilio_service: TwilioService,
        knowledge_base_service: KnowledgeBaseService,
        gohighlevel_service: GoHighLevelClient,
        enabled_tools: list[str] | None = None,
    ) -> None:
        self.llm = ChatOpenAI(api_key=settings.open_ai.OPENAI_API_KEY, model=settings.open_ai.CHAT_MODEL)
        self.twilio_service = twilio_service
        self.knowledge_base_service = knowledge_base_service
        self.gohighlevel_service = gohighlevel_service
        self.last_user_phone = None
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
            "create_contact": self.create_contact,
            "update_contact_info": self.update_contact_info,
            "get_free_appointment_slots": self.get_free_appointment_slots,
            "create_appointment": self.create_appointment,
            "wait_for": self.wait_for,
            "get_phone_number": self.get_phone_number,
        }
        return {k: v for k, v in mapping.items() if k in self.enabled_tools}

    async def get_service_details(self, query: str, *args, **kwargs) -> str:
        return await self.knowledge_base_service.retrieve(query)

    async def finish_the_call(self, call_sid: str, *args, **kwargs) -> None:
        return await self.twilio_service.handle_end_call(call_sid=call_sid)

    async def redirect_to_manager(self, call_sid: str, *args, **kwargs) -> None:
        return await self.twilio_service.redirect_to_manager(call_sid=call_sid)

    async def create_contact(
        self,
        firstName: str,
        lastName: str,
        phone: str,
        companyName: str,
        tags: list[GoHighLevel] = [GoHighLevel.FROM_AIZEN],
        customFields: list[CustomFieldSchema] | None = None,
    ) -> ContactDetail:
        return await self.gohighlevel_service.create_contact(
            firstName=firstName, lastName=lastName, phone=phone, companyName=companyName, tags=tags, customFields=customFields
        )

    async def update_contact_info(
        self,
        contact_id: str,
        firstName: str | None = None,
        lastName: str | None = None,
        phone: str | None = None,
        companyName: str | None = None,
        tags: list[GoHighLevel] | None = None,
        customFields: list[CustomFieldSchema] | None = None,
    ):
        return await self.gohighlevel_service.update_contact(contact_id, firstName, lastName, phone, companyName, tags, customFields)

    async def get_free_appointment_slots(self, startDate: str, endDate: str):
        return await self.gohighlevel_service.get_free_slots(startDate, endDate)

    async def create_appointment(self, startTime: str, **kwargs):
        return await self.gohighlevel_service.create_appointment(startTime)
    
    async def wait_for(self, seconds: int, *args, **kwargs) -> None:
        self.log(f"[DEBUG] Waiting silently for {seconds} seconds...")
        await asyncio.sleep(seconds)
        self.log(f"[DEBUG] Done waiting.")
        return "wait_completed"
    
    async def get_phone_number(self, transcript: str):
        match = re.search(r"\+\d{9,15}", transcript)
        if match:
            self.last_user_phone = match.group(0)
        return {"lastUserPhone": self.last_user_phone}
