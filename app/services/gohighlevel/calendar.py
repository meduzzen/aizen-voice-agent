from app.core.config.config import settings
from app.schemas.gohighlevel.calendar import AvailableSlots, CalendarCreate, CalendarInfo, CalendarsResponse, DateSlots
from app.services.gohighlevel.gohighlevel import GoHighLevelService


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
    