from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import NoDecode

from app.core.config.base import BaseConfig


class AppBaseConfig(BaseConfig):
    PROJECT_NAME: str = "Agent_Ava"
    HOST: str
    PORT: int
    RELOAD: bool
    ALLOWED_ORIGINS: Annotated[list[str], NoDecode]
    WORKERS: int = Field(1, alias="UV_WORKERS")
    COMPANY_NAME: str = Field(..., alias="COMPANY_NAME")
    TRUST_ACCOUNT_NAME: str = Field(..., alias="TRUST_ACCOUNT_NAME")
    BSB: str = Field(..., alias="BSB")
    ACCOUNT_NUMBER: str = Field(..., alias="ACCOUNT_NUMBER")
    PUBLIC_HOST: str | None = None

    @field_validator("ALLOWED_ORIGINS", mode="before")
    def parse_allowed_origins(cls, value: str) -> list[str]:
        return value.split(",")

    def base_url(self, scheme: str) -> str:
        return f"{scheme}://{self.HOST}:{self.PORT}"
