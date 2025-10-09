from typing import Annotated
from datetime import datetime

from pydantic import BaseModel, RootModel, BeforeValidator
from app.utils.iso_to_unix import convert_iso_to_unix


class DateSlots(BaseModel):
    slots: list[str]


class AvailableSlots(RootModel):
    root: dict[str, DateSlots]


class CalendarInfo(BaseModel):
    calendarId: str
    startDate: Annotated[int, BeforeValidator(convert_iso_to_unix)]
    endDate: Annotated[int, BeforeValidator(convert_iso_to_unix)]


class OpenHour(BaseModel):
    openHour: int | None = None
    openMinute: int | None = None
    closeHour: int | None = None
    closeMinute: int | None = None


class OpenHours(BaseModel):
    daysOfTheWeek: list[int]
    hours: list[OpenHour] = []

class TeamMember(BaseModel):
    userId: str
    priority: float | None = None
    isPrimary: bool | None = None


class CalendarDetails(BaseModel):
    id: str
    name: str
    groupId: str | None = None
    teamMembers: list[TeamMember] | None = None
    openHours: list[OpenHours] | None = None


class CalendarsResponse(BaseModel):
    calendars: list[CalendarDetails]


class CalendarCreate(BaseModel):
    isActive: bool
    groupId: str | None = None
    teamMembers: list[TeamMember]
    eventType: str
    name: str
    description: str | None = None
    calendarType: str
    openHours: list[OpenHours]
