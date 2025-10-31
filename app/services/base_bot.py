import asyncio
import json
import uuid
from abc import ABC, abstractmethod
from contextlib import suppress

import websockets
from fastapi import WebSocket, WebSocketDisconnect

from app.core.config.config import settings
from app.core.config.prompts import Prompts
from app.core.mixins import LogMixin
from app.schemas.config import SessionConfig
from app.schemas.events import EventType, OpenAIEvents
from app.schemas.summary import Speaker
from app.services.gohighlevel.client import GoHighLevelClient
from app.services.openai_realtime import OpenAIRealtimeService
from app.services.summary import SummaryService
from app.services.tool_service import ToolService
from app.services.transcription import TranscriptionService


class AbstractBotService(ABC):
    @abstractmethod
    async def initialize_config(self) -> None:
        pass

    @abstractmethod
    async def initialize_init_messages(self) -> None:
        pass

    # @abstractmethod
    # async def handle_media_stream(self, ws: WebSocket) -> None:
    #     pass


class BaseBotService(AbstractBotService, LogMixin):
    def __init__(
        self,
        summary_service: SummaryService,
        transcription_service: TranscriptionService,
        openai_service: OpenAIRealtimeService,
        tool_service: ToolService,
        gohighlevel_service: GoHighLevelClient,
    ) -> None:
        super().__init__()
        self.session_id = uuid.uuid4()
        self.stream_sid = None
        self.last_assistant_item = None

        self.summary_service = summary_service
        self.transcription_service = transcription_service
        self.openai_service = openai_service
        self.tool_service = tool_service
        self.gohighlevel_service = gohighlevel_service
        self.tool_service.set_current_session(self.session_id)

    async def initialize_config(self) -> None:
        session_config = SessionConfig(
            instructions=Prompts.SYSTEM_PROMPT,
            tools=[],
        )
        self.openai_service.update_session_config(session_config)

    async def handle_media_stream(self, ws: WebSocket) -> None:
        await ws.accept()
        await self.initialize_config()
        await self.initialize_init_messages()

        async with websockets.connect(
            f"{settings.open_ai.WSS_REALTIME}{settings.open_ai.WSS_REALTIME_MODEL}",
            additional_headers=settings.open_ai.realtime_headers,
        ) as openai_ws:
            try:
                await self.openai_service.send_session_update(websocket=openai_ws)
                await self.openai_service.send_initial_message(websocket=openai_ws)
                await asyncio.gather(
                    self._send_to_websocket(openai_ws, ws=ws),
                    self._receive_from_websocket(openai_ws, ws=ws),
                )
            finally:
                if self.gohighlevel_service.contact_id is not None:
                    try:
                        await self.gohighlevel_service.update_contact_custom_fields(self.session_id)
                    except Exception as e:
                        self.log(f"Failed to update contact {self.gohighlevel_service.contact_id}: {str(e)}")
                else:
                    self.log("No contact was created during this session. Skipping transcript update.")

                with suppress(RuntimeError):
                    await ws.send_text("Session finished")
                with suppress(RuntimeError):
                    await ws.close()

    async def proceed_user_interruption(self, openai_ws: websockets.ClientConnection, ws: WebSocket) -> None:
        if self.last_assistant_item:
            self.log(f"[BOT] Interrupting item: {self.last_assistant_item}")
            await self._handle_speech_started_event(openai_ws=openai_ws, ws=ws)

    async def proceed_sending_media(self, response: dict, ws: WebSocket) -> None:
        audio_delta = {
            "event": EventType.MEDIA,
            "streamSid": self.stream_sid,
            "media": {"payload": response["delta"]},
        }
        try:
            await ws.send_json(audio_delta)
            await ws.send_json({"event": EventType.MARK, "streamSid": self.stream_sid})
        except RuntimeError:
            return

        if item_id := response.get("item_id"):
            self.last_assistant_item = item_id

    async def execute_tool(self, data: dict, openai_ws: websockets.ClientConnection) -> None:
        tool_name = data.get("name")
        arguments = json.loads(data.get("arguments"))

        self.log(f"[TOOL EXECUTION] Executing the tool: {tool_name} with arguments: {arguments}")

        tool = self.tool_service.tool_mapping.get(tool_name)
        if tool:
            result = await tool(**arguments)
            await self.openai_service.generate_audio_response(self.stream_sid, openai_ws, result, tool_name=tool_name)

    async def _send_to_websocket(self, openai_ws: websockets.ClientConnection, ws: WebSocket) -> None:
        try:
            async for openai_message in openai_ws:
                response = json.loads(openai_message)
                event_type = response.get("type")

                if event_type == OpenAIEvents.ASSISTANT_TRANSCRIPT:
                    await self.transcription_service.proceed_transcription(
                        response=response,
                        speaker=Speaker.ASSISTANT,
                        session_id=self.session_id,
                    )

                if event_type == OpenAIEvents.AUDIO_DELTA and "delta" in response:
                    await self.proceed_sending_media(response=response, ws=ws)

                if event_type == OpenAIEvents.CLIENT_TRANSCRIPT:
                    await self.transcription_service.proceed_transcription(
                        response=response,
                        speaker=Speaker.CLIENT,
                        session_id=self.session_id,
                    )

                    transcript = response.get("transcript", "")
                    if transcript:
                        await self.tool_service.get_phone_number(transcript)

                if event_type == OpenAIEvents.SPEECH_STARTED:
                    await self.proceed_user_interruption(openai_ws=openai_ws, ws=ws)

                if event_type == OpenAIEvents.TOOL_CALL:
                    self.log(f"[TOOL_CALL] Full data: {json.dumps(response, indent=2)}")
                    await self.execute_tool(data=response, openai_ws=openai_ws)

        except (websockets.ConnectionClosedOK, websockets.ConnectionClosedError) as e:
            self.log(f"[OPENAI_WS] Connection closed: {e}")
        except Exception as e:
            self.log(f"[ERROR] Exception in _send_to_websocket: {e}")

    def parsing_start_data(self, start_data: dict) -> None:
        self.stream_sid = start_data.get("streamSid")
        self.log(f"[TWILIO] Stream START. streamSid={self.stream_sid}")

    def reset_stream(self, data: dict) -> None:
        self.parsing_start_data(data["start"])
        self.last_assistant_item = None

    async def _receive_from_websocket(self, openai_ws: websockets.ClientConnection, ws: WebSocket) -> None:
        try:
            async for message in ws.iter_text():
                data = json.loads(message)
                event_type = data.get("event")

                if event_type == EventType.MEDIA:
                    await self.openai_service.audio_append(websocket=openai_ws, audio_base64=data["media"]["payload"])

                if event_type == EventType.START:
                    self.reset_stream(data=data)  # TODO: parse data to pydantic schema

        except WebSocketDisconnect:
            self.log("[WEBSOCKET] Client disconnected.")
        except Exception as e:
            self.log(f"[ERROR] _receive_from_websocket: {e}")
        finally:
            with suppress(Exception):
                await self.openai_service.close(websocket=openai_ws)

    async def _handle_speech_started_event(self, openai_ws: websockets.ClientConnection, ws: WebSocket) -> None:
        self.log("Handling speech started event.")

        await self.openai_service.send_conversation_truncate(
            last_assistant_item=self.last_assistant_item,
            websocket=openai_ws,
        )
        await ws.send_json({"event": "clear", "streamSid": self.stream_sid})
        self.last_assistant_item = None
