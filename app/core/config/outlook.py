from pydantic import Field

from app.core.config.base import BaseConfig


class OutlookConfig(BaseConfig):
    TENANT_ID: str = Field("", alias="OUTLOOK_TENANT_ID")
    CLIENT_ID: str = Field("", alias="OUTLOOK_CLIENT_ID")
    CLIENT_SECRET: str = Field("", alias="OUTLOOK_CLIENT_SECRET")
    SENDER_UPN: str = Field("", alias="OUTLOOK_SENDER_UPN")

    AUTHORITY: str = Field(default="")
    SCOPE: str = Field(default="https://graph.microsoft.com/.default")
    GRAPH_BASE: str = Field(default="https://graph.microsoft.com/v1.0")

    def authority(self) -> str:
        return self.AUTHORITY or f"https://login.microsoftonline.com/{self.TENANT_ID}"
