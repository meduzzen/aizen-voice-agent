import base64

from elevenlabs.client import AsyncElevenLabs
from fastapi import WebSocket

from app.core.config.config import settings
from app.core.mixins import LogMixin
from app.schemas.events import EventType


class ElevenLabsService(LogMixin):
    def __init__(self):
        self.elevenlabs_client = AsyncElevenLabs(api_key=settings.elevenlabs.ELEVENLABS_API_KEY)

    async def streaming(self, text: str, stream_sid: str, ws: WebSocket, previous_message: str = "") -> None:
        async for chunk in self.elevenlabs_client.text_to_speech.stream(
            voice_id=settings.elevenlabs.ELEVENLABS_VOICE_ID,
            previous_text=previous_message,
            text=text,
            output_format=settings.elevenlabs.ELEVENLABS_OUTPUT_FORMAT,
            optimize_streaming_latency=settings.elevenlabs.ELEVENLABS_STREAMING_LATENCY,
            model_id=settings.elevenlabs.ELEVENLABS_MODEL_ID,
        ):
            audio_delta = {
                "event": EventType.MEDIA,
                "streamSid": stream_sid,
                "media": {"payload": base64.b64encode(chunk).decode()},
            }
            await ws.send_json(audio_delta)
