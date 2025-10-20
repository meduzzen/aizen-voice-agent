from app.core.config.config import settings
from app.core.config.enums import GoHighLevel
from app.schemas.gohighlevel.calendar import CalendarCreate
from app.schemas.gohighlevel.contact import CustomFieldSchema
from app.services.gohighlevel.appointment import Appointment
from app.services.gohighlevel.calendar import Calendar
from app.services.gohighlevel.contact import Contact
from app.services.summary import SummaryService


class GoHighLevelClient:
    def __init__(
        self, contact_service: Contact, appointment_service: Appointment, calendar_service: Calendar, summary_service: SummaryService
    ):
        self.contact_service = contact_service
        self.appointment_service = appointment_service
        self.calendar_service = calendar_service
        self.summary_service = summary_service

        self.contact_id: str | None = None

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
    ):
        contact_data = await self.contact_service.create_contact(
            firstName=firstName,
            lastName=lastName,
            phone=phone,
            companyName=companyName,
            tags=tags,
            customFields=customFields,
        )

        if contact_data.get("is_duplicate"):
            self.contact_id = contact_data.get("existing_contact_id")
        elif contact_data.get("contact_id"):
            self.contact_id = contact_data.get("contact_id")

        return contact_data

    async def update_contact(
        self,
        contact_id: str | None = None,
        firstName: str | None = None,
        lastName: str | None = None,
        phone: str | None = None,
        companyName: str | None = None,
        tags: list[GoHighLevel] | None = None,
        customFields: list[CustomFieldSchema] | None = None,
        *args,
        **kwargs,
    ):
        return await self.contact_service.update_contact(
            contact_id=contact_id if contact_id else self.contact_id,
            firstName=firstName,
            lastName=lastName,
            phone=phone,
            companyName=companyName,
            tags=tags,
            customFields=customFields,
        )

    async def delete_contact(self):
        await self.contact_service.delete_contact(self.contact_id)
        self.contact_id = None

    async def create_appointment(self, startTime: str):
        appointment = await self.appointment_service.create_appointment(self.contact_id, startTime)
        await self.contact_service.update_contact(contact_id=self.contact_id, tags=[GoHighLevel.ALREADY_BOOKED])
        return appointment

    async def delete_appointment(self, appointment_id: str):
        return await self.appointment_service.delete_appointment(appointment_id)

    async def create_calendar(self, calendar_info: CalendarCreate):
        return await self.calendar_service.create_calendar(calendar_info)

    async def get_calendars(self):
        return await self.calendar_service.get_calendars()

    async def get_free_slots(self, startDate: str, endDate: str):
        return await self.calendar_service.get_free_slots(startDate, endDate)

    async def update_contact_custom_fields(self, session_id):
        messages = self.summary_service.get_full_transcript(session_id)
        transcript_text = "\n".join([f"{m.type}: {m.content}" for m in messages])

        custom_fields = [
            CustomFieldSchema(
                id=settings.gohighlevel.CUSTOM_FIELDS_ID, key=settings.gohighlevel.CUSTOM_FIELDS_KEY, field_value=transcript_text
            )
        ]

        await self.contact_service.update_contact(contact_id=self.contact_id, customFields=custom_fields)
