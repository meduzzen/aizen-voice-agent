import re
from asyncio import gather, sleep, to_thread
from datetime import datetime
from typing import Callable
from uuid import UUID

import pytz
from langchain_openai import ChatOpenAI

from app.core import settings
from app.core.config.enums import GoHighLevel
from app.core.mixins import LogMixin
from app.schemas.contact import ContactSchema
from app.schemas.gohighlevel.appointment import ConvertTimeRequest
from app.schemas.gohighlevel.contact import ContactDetail, CustomFieldSchema
from app.services.gohighlevel.client import GoHighLevelClient
from app.services.knowledge_base import KnowledgeBaseService
from app.services.summary import SummaryService
from app.services.twilio_service import TwilioService
from app.utils.format_transcript import format_transcript
from app.core.config.prompts import Prompts


class ToolService(LogMixin):
    def __init__(
        self,
        twilio_service: TwilioService,
        knowledge_base_service: KnowledgeBaseService,
        gohighlevel_service: GoHighLevelClient,
        summary_service: SummaryService,
        enabled_tools: list[str] | None = None,
    ) -> None:
        self.llm = self.get_llm()
        self.twilio_service = twilio_service
        self.knowledge_base_service = knowledge_base_service
        self.gohighlevel_service = gohighlevel_service
        self.summary_service = summary_service
        self.last_user_phone = None
        self.current_session_id: UUID | None = None
        self.enabled_tools = enabled_tools or [
            "get_service_details",
            "finish_the_call",
            "redirect_to_manager",
        ]
        
    @staticmethod
    def get_llm():
        llm = ChatOpenAI(model=settings.open_ai.CHAT_MODEL, api_key=settings.open_ai.OPENAI_API_KEY)
        return llm.with_structured_output(ContactSchema)
        
    def set_current_session(self, session_id: UUID) -> None:
        self.current_session_id = session_id

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
            "convert_time": self.convert_time_tool,
            "get_contact_info": self.get_contact_info,
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
        *args,
        **kwargs,
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
        *args,
        **kwargs,
    ):
        return await self.gohighlevel_service.update_contact(
            contact_id=contact_id,
            firstName=firstName,
            lastName=lastName,
            phone=phone,
            companyName=companyName,
            tags=tags,
            customFields=customFields,
        )

    async def get_free_appointment_slots(self, startDate: str, endDate: str, *args, **kwargs):
        return await self.gohighlevel_service.get_free_slots(startDate, endDate)

    async def create_appointment(self, startTime: str, *args, **kwargs):
        return await self.gohighlevel_service.create_appointment(startTime)

    async def wait_for(self, seconds: int, *args, **kwargs) -> str:
        self.log(f"[DEBUG] Waiting silently for {seconds} seconds...")
        await sleep(seconds)
        self.log("[DEBUG] Done waiting.")
        return "wait_completed"
    
    async def get_contact_info(self):
        if not self.current_session_id:
            raise ValueError("Current session not set")
        
        transcript = self.summary_service.get_full_transcript(session_id=self.current_session_id)
        
        if not transcript:
            raise ValueError("No transcript found for this session")
        
        self.log(f'TRANSCRIPT: {transcript}')
        formatted_transcript = format_transcript(transcript)
        
        result = await self.llm.ainvoke(
            Prompts.EXTRACT_CONTACT_INFO.format(formatted_transcript=formatted_transcript)
        )
        
        self.log(f"EXTRACTION RESULT: {result}")
        return result.model_dump()

    async def get_phone_number(self, transcript: str):
        cleaned = re.sub(r"[^\d+]", "", transcript)
        
        if not cleaned.startswith("+"):
            digits = re.sub(r"\D", "", cleaned)
            cleaned = f"+{digits}"
        
        if 9 <= len(re.sub(r"\D", "", cleaned)) <= 15:
            self.last_user_phone = cleaned
        else:
            self.last_user_phone = None
        
        return {"lastUserPhone": self.last_user_phone}

    @staticmethod
    def convert_time(time: str, timezone: str, output_format: str | None = "%Y-%m-%dT%H:%M:%S%z") -> str:
        request = ConvertTimeRequest(time_utc=time, timezone=timezone, output_format=output_format)
        dt_utc = datetime.fromisoformat(request.time_utc.replace("Z", "+00:00"))
        tz = pytz.timezone(request.timezone)
        dt_local = dt_utc.astimezone(tz)
        return dt_local.strftime(request.output_format)

    async def convert_time_tool(self, time_utc: list[str] | str, timezone: str, *args, **kwargs) -> list[str] | dict[str, str] | str:
        try:
            if isinstance(time_utc, str):
                return await to_thread(self.convert_time, time_utc, timezone)
            return await gather(*[to_thread(self.convert_time, t, timezone) for t in time_utc])
        except Exception as e:
            return {"error": str(e)}
