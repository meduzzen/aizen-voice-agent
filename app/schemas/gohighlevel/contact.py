from openai import BaseModel
from pydantic import ConfigDict, Field

from app.schemas.summary import MessageSchema


class CustomFieldSchema(BaseModel):
    id: str
    key: str | None = None
    field_value: str = Field(alias="fieldValue")

    model_config = ConfigDict(populate_by_name=True)


class TranscriptData(BaseModel):
    messages: list[MessageSchema] = Field(default_factory=list)


class ContactBase(BaseModel):
    firstName: str
    lastName: str
    phone: str
    companyName: str = Field(..., alias="companyName")
    tags: list[str] = ["From AIZen"]
    customFields: list[CustomFieldSchema] | None = None


class ContactUpdate(BaseModel):
    firstName: str | None = None
    lastName: str | None = None
    phone: str | None = None
    companyName: str | None = None
    tags: list[str] | None = None
    customFields: list[CustomFieldSchema] | None = None


class ContactDetail(BaseModel):
    contact_id: str = Field(..., alias="id")
    firstName: str = Field(..., alias="firstName")
    lastName: str = Field(..., alias="lastName")
    phone: str
    companyName: str = Field(..., alias="companyName")
    tags: list[str] = ["From AIZen"]
    customFields: list[CustomFieldSchema] | None = None
