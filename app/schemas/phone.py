import re
from pydantic import BaseModel, Field, field_validator


class PhoneSchema(BaseModel):
    lastUserPhone: str | None = Field(None, description="Validated phone number in international format")
    
    @field_validator('lastUserPhone', mode='before')
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        if v is None or v == "":
            return None
        
        cleaned = re.sub(r"[^\d+]", "", v)
        
        if not cleaned.startswith("+"):
            digits = re.sub(r"\D", "", cleaned)
            cleaned = f"+{digits}"
        
        digit_count = len(re.sub(r"\D", "", cleaned))
        if 9 <= digit_count <= 15:
            return cleaned
        
        return None
