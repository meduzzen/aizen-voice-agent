from pydantic import Field

from app.core.config.base import BaseConfig


class TwilioConfig(BaseConfig):
    TWILIO_ACCOUNT_SID: str = Field(..., alias="TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: str = Field(..., alias="TWILIO_AUTH_TOKEN")
    REDIRECT_PHONE_NUMBER: str = Field(..., alias="REDIRECT_PHONE_NUMBER")
    CALLER_ID: str = Field("", alias="CALLER_ID")
    TWILIO_NUMBER: str = Field("", alias="TWILIO_NUMBER")
    TWILIO_VOICE: str = Field("", alias="TWILIO_VOICE")
