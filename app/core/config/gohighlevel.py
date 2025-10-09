from pydantic import Field

from app.core.config.base import BaseConfig

class GoHighLevelConfig(BaseConfig):
    TOKEN_GOHIGHLEVEL: str = Field(..., alias="TOKEN_GOHIGHLEVEL")
    LOCATION_ID: str = Field(..., alias="LOCATION_ID")
    CALENDAR_ID: str = Field(..., alias="CALENDAR_ID")
    CUSTOM_FIELDS_ID: str = Field(..., alias="CUSTOM_FIELDS_ID")
    CUSTOM_FIELDS_KEY: str = Field(..., alias="CUSTOM_FIELDS_KEY")
    