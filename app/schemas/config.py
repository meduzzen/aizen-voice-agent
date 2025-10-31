from typing import Any
from pydantic import BaseModel, Field

from app.core import settings
from app.core.config.prompts import Prompts


class Parameter(BaseModel):
    type: str = Field(default="object")
    properties: dict[str, dict]
    required: list[str]


class Tool(BaseModel):
    type: str = Field(default="function")
    name: str
    description: str
    parameters: Parameter | None = None


class SessionConfig(BaseModel):
    input_audio_format: str = Field(default=settings.open_ai.INPUT_AUDIO_FORMAT)
    output_audio_format: str = Field(default=settings.open_ai.OUTPUT_AUDIO_FORMAT)
    turn_detection: dict[str, Any] = Field(default={"type": "server_vad", "threshold": 0.7})
    voice: str = Field(default=settings.open_ai.VOICE)
    instructions: str
    modalities: list[str] = Field(default=["text", "audio"])
    temperature: float = Field(default=settings.open_ai.TEMPERATURE)
    input_audio_transcription: dict[str, str] = Field(
        default={
            "model": settings.open_ai.TRANSCRIPTION_MODEL,
            "prompt": Prompts.TRANSCRIPTION_PROMPT,
        }
    )
    input_audio_noise_reduction: dict[str, str] = Field(default={"type": "far_field"})
    tools: list[Tool] = Field(default_factory=list)


class InitMessage(BaseModel):
    type: str = Field(default="input_text")
    text: str


class InitMessages(BaseModel):
    messages: list[InitMessage]
