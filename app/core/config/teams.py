from pydantic import Field

from app.core.config.base import BaseConfig


class TeamsConfig(BaseConfig):
    WEBHOOK_URL: str = Field("", alias="TEAMS_WEBHOOK_URL")
