import json
from contextlib import suppress
from typing import Any

import websockets

from app.core.config.prompts.web_bot import Prompts
from app.core.mixins import LogMixin
from app.schemas.config import InitMessages, SessionConfig


class OpenAIRealtimeService(LogMixin):
    """
    Handles OpenAI Realtime WebSocket communication.
    Responsible only for:
      - Connecting to OpenAI's Realtime API
      - Sending/receiving events
    """

    def __init__(self, session_config: SessionConfig | None = None, init_messages: InitMessages | None = None):
        self._session_config = session_config
        self._init_messages = init_messages

    def update_session_config(self, session_config: SessionConfig):
        self._session_config = session_config

    def update_init_messages(self, init_messages: InitMessages):
        self._init_messages = init_messages

    @staticmethod
    async def close(websocket: websockets.ClientConnection):
        """Close the OpenAI WebSocket."""
        with suppress(Exception):
            await websocket.close()

    @staticmethod
    async def audio_append(websocket: websockets.ClientConnection, audio_base64: str) -> None:
        """Send audio chunk to OpenAI."""
        audio_append = {
            "type": "input_audio_buffer.append",
            "audio": audio_base64,
        }
        try:
            await websocket.send(json.dumps(audio_append))
        except (websockets.ConnectionClosedOK, websockets.ConnectionClosedError) as e:
            print(f"[OpenAI_WS] send closed: code={getattr(e, 'code', None)} reason={getattr(e, 'reason', None)}")
            return

    async def send_conversation_truncate(
        self,
        websocket: websockets.ClientConnection,
        last_assistant_item: Any,
    ) -> None:
        """Truncate an assistant's current speech output."""
        if not last_assistant_item:
            self.log("No assistant item to truncate.")
            return

        truncate_event = {
            "type": "conversation.item.truncate",
            "item_id": last_assistant_item,
            "content_index": 0,
        }
        await websocket.send(json.dumps(truncate_event))

    @property
    def session_config(self) -> dict:
        return self._session_config.model_dump()

    @property
    def init_messages(self) -> list[dict]:
        return self._init_messages.model_dump().get("messages")

    async def send_session_update(self, websocket: websockets.ClientConnection) -> None:
        self.log(f"[OpenAI WS] session_config: {self._session_config.model_dump()}")
        await websocket.send(
            json.dumps(
                {
                    "type": "session.update",
                    "session": self.session_config,
                }
            )
        )
        await websocket.send(json.dumps({"type": "response.create"}))

    async def send_initial_message(self, websocket: websockets.ClientConnection) -> None:
        await websocket.send(
            json.dumps(
                {
                    "type": "conversation.item.create",
                    "item": {"type": "message", "role": "assistant", "content": self.init_messages},
                }
            )
        )
        await websocket.send(json.dumps({"type": "response.create"}))

    @staticmethod
    def prepare_instructions(tool_name: str, response_text: str) -> str:
        tool_mapping = {
            "create_contact": Prompts.CREATE_CONTACT_INSTRUCTION,
            "get_free_appointment_slots": Prompts.GET_SLOTS_INSTRUCTION,
            "create_appointment": Prompts.CREATE_APPOINTMENT_INSTRUCTION,
            "get_service_details": Prompts.GET_SERVICE_DETAILS_INSTRUCTION,
            "wait_for": Prompts.WAIT_FOR_PHONE_INSTRUCTION,
            "get_phone_number": Prompts.GET_PHONE_NUMBER_INSTRUCTION,
        }

        duplicate_text = (
            "Oh, it looks like you're already in our database, happy to see you again! "
            "Would you like to schedule a call with our team to discuss your project in detail?"
            if tool_name == "create_contact" and isinstance(response_text, dict) and response_text.get("is_duplicate")
            else ""
        )

        instructions_template = tool_mapping.get(tool_name, Prompts.TOOL_RESULT_INSTRUCTION)
        return instructions_template.format(response_text=response_text, duplicate_text=duplicate_text)

    async def generate_audio_response(
        self,
        stream_id: str,
        websocket: websockets.ClientConnection,
        response_text: str,
        tool_name: str = None,
    ) -> None:
        try:
            self.log(f"[TOOL PROCESSING] Starting generate_audio_response for call_id={stream_id}, tool={tool_name}")

            response_message = {
                "type": "conversation.item.create",
                "item": {
                    "type": "function_call_output",
                    "call_id": stream_id,
                    "output": response_text,
                },
            }

            await websocket.send(json.dumps(response_message))

            instructions = self.prepare_instructions(tool_name, response_text)
            response_create = {
                "type": "response.create",
                "response": {"modalities": ["text", "audio"], "instructions": instructions},
            }
            await websocket.send(json.dumps(response_create))

        except (websockets.ConnectionClosedOK, websockets.ConnectionClosedError) as e:
            self.log(f"[ERROR] WebSocket closed during generate_audio_response: {e}")
            raise
        except Exception as e:
            self.log(f"[ERROR] Exception in generate_audio_response: {e}")
            raise
