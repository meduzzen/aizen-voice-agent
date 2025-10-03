from enum import StrEnum

from pydantic import BaseModel


class Speaker(StrEnum):
    CLIENT = "Client"
    ASSISTANT = "Assistant"


class MessageSchema(BaseModel):
    type: str
    content: str


class SummarySchema(BaseModel):
    client_name: str
    conversation_summary: str
    phone_number: str | None = ""
