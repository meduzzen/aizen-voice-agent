from pydantic import Field

from app.core.config.base import BaseConfig


class N8NConfig(BaseConfig):
    N8N_WEBHOOK_URL: str = Field("", alias="N8N_WEBHOOK_URL")
