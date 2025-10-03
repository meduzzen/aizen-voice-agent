from app.core.config.ai import OpenAIConfig
from app.core.config.app import AppBaseConfig
from app.core.config.base import BaseConfig
from app.core.config.elevenlabs import ElevenLabsConfig
from app.core.config.n8n import N8NConfig
from app.core.config.outlook import OutlookConfig
from app.core.config.teams import TeamsConfig
from app.core.config.twilio import TwilioConfig
from app.core.config.vector_db import VectorDBBaseConfig

__all__ = ["Settings", "settings"]


class Settings(BaseConfig):
    """
    A centralized Settings class that aggregates different configuration
    components like database, authentication, S3 settings etc.
    """

    app: AppBaseConfig = AppBaseConfig()
    open_ai: OpenAIConfig = OpenAIConfig()
    twilio: TwilioConfig = TwilioConfig()
    teams: TeamsConfig = TeamsConfig()
    n8n: N8NConfig = N8NConfig()
    outlook: OutlookConfig = OutlookConfig()
    vector_bd: VectorDBBaseConfig = VectorDBBaseConfig()
    elevenlabs: ElevenLabsConfig = ElevenLabsConfig()


settings = Settings()
