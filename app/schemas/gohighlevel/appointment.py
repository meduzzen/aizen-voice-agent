from datetime import datetime
from typing import Annotated, Union

from pydantic import BaseModel, BeforeValidator, Field


def validate_date(value: Union[datetime, str]) -> str:
    if isinstance(value, datetime):
        return value.isoformat()
    elif isinstance(value, str):
        return value


ISODateTime = Annotated[str, BeforeValidator(validate_date)]


class AppointmentBase(BaseModel):
    calendarId: str
    contactId: str
    startTime: ISODateTime
    endTime: ISODateTime | None = None
    title: str = "Booked by AIZen"


class AppointmentUpdate(BaseModel):
    calendarId: str | None = None
    contactId: str | None = None
    startTime: ISODateTime | None = None
    endTime: ISODateTime | None = None
    title: str | None = None


class AppointmentDetails(BaseModel):
    appointmentId: str = Field(..., alias="id")


class ConvertTimeRequest(BaseModel):
    time_utc: str
    timezone: str
    output_format: str | None = "%Y-%m-%dT%H:%M:%S%z"
