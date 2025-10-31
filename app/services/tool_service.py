import pytz
from asyncio import gather, sleep, to_thread
from datetime import datetime
from typing import Callable
from uuid import UUID


from app.core.config.enums import GoHighLevel
from app.core.mixins import LogMixin
from app.core.mixins.llm import LLMMixin
from app.schemas.contact import ContactSchema
from app.schemas.gohighlevel.appointment import ConvertTimeRequest
from app.schemas.gohighlevel.contact import ContactDetail, CustomFieldSchema
from app.schemas.phone import PhoneSchema
from app.services.gohighlevel.client import GoHighLevelClient
from app.services.knowledge_base import KnowledgeBaseService
from app.services.summary import SummaryService
from app.services.twilio_service import TwilioService
from app.utils.format_transcript import format_transcript
from app.core.config.prompts.web_bot import Prompts


class ToolService(LogMixin, LLMMixin):
    def __init__(
        self,
        twilio_service: TwilioService,
        knowledge_base_service: KnowledgeBaseService,
        gohighlevel_service: GoHighLevelClient,
        summary_service: SummaryService,
        enabled_tools: list[str] | None = None,
    ) -> None:
        self.llm = self.get_llm(ContactSchema)
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
        customFields: list[CustomFieldSchema] | None = None,
        *args,
        **kwargs,
    ) -> ContactDetail:
        contact_info = await self.get_contact_info()
        return await self.gohighlevel_service.create_contact(
            firstName=contact_info.firstName,
            lastName=contact_info.lastName,
            phone=contact_info.phone,
            companyName=contact_info.companyName,
            tags=[GoHighLevel.FROM_AIZEN],
            customFields=customFields
        )

    async def update_contact_info(
        self,
        contact_id: str,
        tags: list[GoHighLevel] | None = None,
        customFields: list[CustomFieldSchema] | None = None,
        *args,
        **kwargs,
    ):
        contact_info = await self.get_contact_info()
        return await self.gohighlevel_service.update_contact(
            contact_id=contact_id,
            firstName=contact_info.firstName,
            lastName=contact_info.lastName,
            phone=contact_info.phone,
            companyName=contact_info.companyName,
            tags=tags,
            customFields=customFields,
        )
            
    @staticmethod
    def convert_time(time: str, timezone: str, output_format: str | None = "%Y-%m-%dT%H:%M:%S%z") -> str:
        request = ConvertTimeRequest(time_utc=time, timezone=timezone, output_format=output_format)
        dt_utc = datetime.fromisoformat(request.time_utc.replace("Z", "+00:00"))
        tz = pytz.timezone(request.timezone)
        dt_local = dt_utc.astimezone(tz)
        return dt_local.strftime(request.output_format)
    
    async def get_free_appointment_slots(self, startDate: str, endDate: str, timezone: str, *args, **kwargs):
        try:
            utc_slots = await self.gohighlevel_service.get_free_slots(startDate, endDate)
            
            if not utc_slots or isinstance(utc_slots, dict) and "error" in utc_slots:
                return {"error": "Failed to retrieve available slots"}
            
            flat_slots = []
            if isinstance(utc_slots, dict):
                for _, date_value in utc_slots.items():
                    if isinstance(date_value, dict) and "slots" in date_value:
                        flat_slots.extend(date_value["slots"])
                    elif isinstance(date_value, list):
                        flat_slots.extend(date_value)
            elif isinstance(utc_slots, list):
                flat_slots = utc_slots
            
            if flat_slots:
                converted_slots = await gather(*[
                    to_thread(self.convert_time, slot, timezone) 
                    for slot in flat_slots
                ])
            else:
                converted_slots = []
            
            return {
                "timezone": timezone,
                "slots": converted_slots,
            }
        
        except Exception as e:
            return {"error": str(e)}
    
    async def create_appointment(self, startTime: str, timezone: str = None, *args, **kwargs):
        try:
            if timezone:
                converted_time = await to_thread(self.convert_time, startTime, timezone)
            else:
                converted_time = startTime
            
            return await self.gohighlevel_service.create_appointment(converted_time)
        
        except Exception as e:
            return {"error": str(e)}

    async def wait_for(self, seconds: int, *args, **kwargs) -> str:
        self.log(f"[DEBUG] Waiting silently for {seconds} seconds...")
        await sleep(seconds)
        self.log("[DEBUG] Done waiting.")
        return "wait_completed"
    
    async def get_contact_info(self):
        if not self.current_session_id:
            self.log("[GET_CONTACT_INFO TOOL] Current session not set")
        
        transcript = self.summary_service.get_full_transcript(session_id=self.current_session_id)
        
        if not transcript:
            self.log("[GET_CONTACT_INFO TOOL] No transcript found for this session")
        
        self.log(f'TRANSCRIPT: {transcript}')
        formatted_transcript = format_transcript(transcript)
        
        result = await self.llm.ainvoke(
            Prompts.EXTRACT_CONTACT_INFO.format(formatted_transcript=formatted_transcript)
        )
        
        self.log(f"EXTRACTION RESULT: {result}")
        return result

    async def get_phone_number(self, transcript: str):
        phone_data = PhoneSchema(lastUserPhone=transcript)
        self.last_user_phone = phone_data.lastUserPhone
        
        return phone_data.model_dump()
