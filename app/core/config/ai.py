from pydantic import Field

from app.core.config.base import BaseConfig


class OpenAIConfig(BaseConfig):
    OPENAI_API_KEY: str = Field(..., alias="OPENAI_API_KEY")
    WSS_REALTIME: str = Field("wss://api.openai.com/v1/realtime?model=", alias="WSS_REALTIME")
    WSS_REALTIME_MODEL: str = Field(..., alias="WSS_REALTIME_MODEL")
    INPUT_AUDIO_FORMAT: str = Field("pcm16", alias="INPUT_AUDIO_FORMAT")
    OUTPUT_AUDIO_FORMAT: str = Field("pcm16", alias="OUTPUT_AUDIO_FORMAT")
    VOICE: str = Field(..., alias="VOICE")
    TEMPERATURE: float = Field(..., alias="TEMPERATURE")
    CHAT_MODEL: str = Field(..., alias="CHAT_MODEL")
    TRANSCRIPTION_MODEL: str = Field(..., alias="TRANSCRIPTION_MODEL")

    @property
    def realtime_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.OPENAI_API_KEY}",
            "OpenAI-Beta": "realtime=v1",
        }
