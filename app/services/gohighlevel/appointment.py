from datetime import datetime

from aiohttp_retry import Union
import pytz
from app.core.config.config import settings
from app.schemas.gohighlevel.appointment import AppointmentBase, AppointmentDetails, AppointmentUpdate
from app.services.gohighlevel.gohighlevel import GoHighLevelService
from app.core.config.enums import GoHighLevel


class Appointment(GoHighLevelService):
    def __init__(self):
        super().__init__()

    async def create_appointment(self, contact_id: str, startTime: str):
        print(contact_id)
        
        if not startTime.endswith('Z'):
            if '+' in startTime:
                dt = datetime.fromisoformat(startTime)
                dt_utc = dt.astimezone(pytz.UTC)
                startTime = dt_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
            else:
                startTime = startTime + 'Z'
        
        payload = AppointmentBase(calendarId=settings.gohighlevel.CALENDAR_ID, contactId=contact_id, startTime=startTime, title=GoHighLevel.APPOINTMENT_TITLE).model_dump()
        payload["locationId"] = settings.gohighlevel.LOCATION_ID

        response_json = await self.send_request("POST", "/calendars/events/appointments", payload)
        self.log(f"Appointment creation raw response: {response_json}")

        if response_json.get('statusCode') == 400:
            raise ValueError(f"Slot unavailable: {response_json.get('message')}")

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
        