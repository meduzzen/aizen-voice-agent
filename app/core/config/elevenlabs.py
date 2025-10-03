from pydantic import Field

from app.core.config.base import BaseConfig


class ElevenLabsConfig(BaseConfig):
    ELEVENLABS_API_KEY: str = Field(..., alias="ELEVENLABS_API_KEY")
    ELEVENLABS_VOICE_ID: str = Field(..., alias="ELEVENLABS_VOICE_ID")
    ELEVENLABS_OUTPUT_FORMAT: str = Field("ulaw_8000", alias="ELEVENLABS_OUTPUT_FORMAT")
    ELEVENLABS_STREAMING_LATENCY: int = Field(2, alias="ELEVENLABS_STREAMING_LATENCY")
    ELEVENLABS_MODEL_ID: str = Field(..., alias="ELEVENLABS_MODEL_ID")
