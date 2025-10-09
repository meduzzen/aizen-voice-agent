from datetime import datetime
import aiohttp
from typing import Union
import pytz

from app.core.config.config import settings
from app.schemas.gohighlevel.appointment import AppointmentBase, AppointmentDetails, AppointmentUpdate
from app.schemas.gohighlevel.calendar import AvailableSlots, CalendarCreate, CalendarInfo, CalendarsResponse, DateSlots
from app.schemas.gohighlevel.contact import ContactBase, ContactDetail, ContactUpdate, CustomFieldSchema
from app.core.mixins import LogMixin


class GoHighLevelService(LogMixin):    
    def __init__(self):
        self.base_url = "https://services.leadconnectorhq.com"
        self.headers = {
            "Authorization": f"Bearer {settings.gohighlevel.TOKEN_GOHIGHLEVEL}",
            "Version": "2021-07-28",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    
    async def send_request(self, method: str, url: str, payload: dict | None = None, headers: dict | None = None, return_status: bool = False
    ) -> dict | tuple[dict, int, str]:
        async with aiohttp.ClientSession(base_url=self.base_url, headers=self.headers) as session:
            async with session.request(method, url, json=payload, headers=headers) as response:
                status_code = response.status
                text = await response.text()
                try:
                    response_json = await response.json()
                except Exception:
                    response_json = {}

                self.log(f"[API] {method} {url} -> {status_code}")
                if text:
                    self.log(f"[API] Response: {text}") 

                if return_status:
                    return response_json, status_code, text
                return response_json
            
            
class Contact(GoHighLevelService):
    def __init__(self):
        super().__init__()

    async def create_contact(self, firstName: str, lastName: str, phone: str, companyName: str, tags: list[str] = ["From AIZen"], customFields: list[CustomFieldSchema] | None = None):
        if customFields is None:
            customFields = [
                CustomFieldSchema(
                    id=settings.gohighlevel.CUSTOM_FIELDS_ID,
                    key=settings.gohighlevel.CUSTOM_FIELDS_KEY,
                    field_value="Conversation will be added here after the call ends."
                )
            ]

        payload = ContactBase(firstName=firstName, lastName=lastName, phone=phone, companyName=companyName, tags=tags, customFields=customFields).model_dump(by_alias=True, exclude_none=True)

        payload["locationId"] = settings.gohighlevel.LOCATION_ID

        self.log(f"[CONTACT] Payload being sent: {payload}")

        response_json, status_code, text = await self.send_request("POST", "/contacts/", payload, return_status=True)

        self.log(f"[CONTACT] Create response ({status_code}): {text[:1000]}")

        if status_code >= 400:
            self.log(f"[ERROR] Failed to create contact: {response_json}", error=True)
            return None

        contact_info = response_json.get("contact", {})
        self.log(f"[CONTACT] Parsed contact info: {contact_info}")

        if not contact_info:
            self.log("[ERROR] Empty contact data in GHL response", error=True)
            return None

        contact_model = ContactDetail(**contact_info).model_dump()
        return contact_model


    async def update_contact(
        self,
        contact_id: str,
        firstName: str | None = None,
        lastName: str | None = None,
        phone: str | None = None,
        companyName: str | None = None,
        tags: list[str] | None = None,
        customFields: list[CustomFieldSchema] | None = None
        ):       
        payload = ContactUpdate(
            firstName=firstName,
            lastName=lastName,
            phone=phone,
            companyName=companyName,
            tags=tags,
            customFields=customFields
            ).model_dump(exclude_none=True)
        data = await self.send_request("PUT", f"/contacts/{contact_id}", payload, self.headers)
        self.log(f"Contact updated: {data}")

    async def delete_contact(self, contact_id: str):
        data = await self.send_request("DELETE", f"/contacts/{contact_id}", headers=self.headers)
        self.log(f"Contact deleted: {data}")

class Appointment(GoHighLevelService):
    def __init__(self):
        super().__init__()

    async def create_appointment(self, contact_id: str, startTime: str):
        print(contact_id)
        
        if startTime.endswith('Z'):
            dt_utc = datetime.fromisoformat(startTime.replace('Z', '+00:00'))
            local_tz = pytz.timezone('Europe/Kyiv')
            dt_local = dt_utc.astimezone(local_tz)
            startTime = dt_local.isoformat()
        elif '+' not in startTime and 'Z' not in startTime:
            startTime = startTime + '+03:00'
        
        payload = AppointmentBase(calendarId=settings.gohighlevel.CALENDAR_ID, contactId=contact_id, startTime=startTime, title="Booked by AIZen"
        ).model_dump()
        payload["locationId"] = settings.gohighlevel.LOCATION_ID

        response_json = await self.send_request("POST", "/calendars/events/appointments", payload)
        self.log(f"Appointment creation raw response: {response_json}")

        appointment_model = AppointmentDetails(**response_json)
        self.log(f"Created Appointment {appointment_model.model_dump()}")
        return appointment_model.model_dump()

    async def update_appointment(
        self,
        appointment_id: str,
        calendarId: str,
        contactId: str,
        startTime: Union[datetime, str] | None = None,
        endTime: Union[datetime, str] | None = None,
        title: str | None = None,
    ):
        payload = AppointmentUpdate(
            calendarId=calendarId, contactId=contactId, startTime=startTime, endTime=endTime, title=title,
        ).model_dump(exclude_none=True)
        await self.send_request("PUT", f"/calendars/events/appointments/{appointment_id}", payload)

    async def delete_appointment(self, appointment_id: str):
        await self.send_request("DELETE", f"/calendars/events/{appointment_id}")


class Calendar(GoHighLevelService):
    def __init__(self):
        super().__init__()

    async def create_calendar(self, calendar_info: CalendarCreate):
        payload = calendar_info.model_dump()
        payload["locationId"] = settings.gohighlevel.LOCATION_ID
        response_json = await self.send_request("POST", "/calendars/", payload)
        self.log(f"Calendar is created: {response_json}")
        return response_json

    async def get_calendars(self):
        response_json = await self.send_request("GET", f"/calendars/?locationId={settings.gohighlevel.LOCATION_ID}")
        self.log(f"Available calendars: {response_json}")
        return CalendarsResponse(**response_json)

    async def get_free_slots(self, startDate: str, endDate: str):
        calendar_info = CalendarInfo(calendarId=settings.gohighlevel.CALENDAR_ID, startDate=startDate, endDate=endDate)
        response_json = await self.send_request(
            "GET",
            f"/calendars/{calendar_info.calendarId}/free-slots?startDate={calendar_info.startDate}&endDate={calendar_info.endDate}",
        )
        self.log(f"{response_json}")
        filtered_slots = {k: v for k, v in response_json.items() if k != "traceId"}
        available_slots = AvailableSlots(root={k: DateSlots(slots=v["slots"]) for k, v in filtered_slots.items()})
        return available_slots.model_dump()


    @staticmethod
    def get_first_slot(available_slots: AvailableSlots) -> str | None:
        for date, date_slots in available_slots.root.items():
            if date_slots.slots:
                return date_slots.slots[0]
        return None

class GoHighLevelClient:
    def __init__(self):
        self.contact_service = Contact()
        self.appointment_service = Appointment()
        self.calendar_service = Calendar()
        self.contact_id: str | None = None

    async def create_contact(self, firstName: str, lastName: str, phone: str, companyName: str, tags: list[str] = ["From AIZen"], customFields: list[CustomFieldSchema] | None = None):
        contact_data = await self.contact_service.create_contact(firstName=firstName, lastName=lastName, phone=phone, companyName=companyName, tags=tags, customFields=customFields,)
        self.contact_id = contact_data.get("contact_id")
        return contact_data

    async def update_contact(
        self,
        firstName: str | None = None,
        lastName: str | None = None,
        phone: str | None = None,
        companyName: str | None = None,
        tags: list[str] | None = None,
        customFields: list[CustomFieldSchema] | None = None
    ):
        return await self.contact_service.update_contact(
            contact_id=self.contact_id,
            firstName=firstName,
            lastName=lastName,
            phone=phone,
            companyName=companyName,
            tags=tags,
            customFields=customFields
        )

    async def delete_contact(self):
        await self.contact_service.delete_contact(self.contact_id)
        self.contact_id = None

    async def create_appointment(self, startTime: str):
        appointment = await self.appointment_service.create_appointment(self.contact_id, startTime)
        await self.contact_service.update_contact(contact_id=self.contact_id, tags=['already booked'])
        return appointment

    async def delete_appointment(self, appointment_id: str):
        return await self.appointment_service.delete_appointment(appointment_id)

    async def create_calendar(self, calendar_info: CalendarCreate):
        return await self.calendar_service.create_calendar(calendar_info)

    async def get_calendars(self):
        return await self.calendar_service.get_calendars()

    async def get_free_slots(self, startDate: str, endDate: str):
        return await self.calendar_service.get_free_slots(startDate, endDate)
    