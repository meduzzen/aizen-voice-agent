import asyncio

from fastapi import Request
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse
from twilio.rest import Client
from twilio.twiml.voice_response import Connect, VoiceResponse

from app.core import settings
from app.core.mixins import LogMixin
from app.schemas.twilio import OutgoingParamsSchema
from app.utils.twilio_sig import validate_twilio_signature


class TwilioService(LogMixin):
    def __init__(self) -> None:
        self.client = Client(settings.twilio.TWILIO_ACCOUNT_SID, settings.twilio.TWILIO_AUTH_TOKEN)
        self.caller_phone_number = None

    @staticmethod
    async def make_call(request: Request) -> OutgoingParamsSchema:
        data = await request.json()
        to_phone_number = data.get("to")

        if not to_phone_number:
            raise HTTPException(status_code=400, detail="The phone number is required")

        client = Client(settings.twilio.TWILIO_ACCOUNT_SID, settings.twilio.TWILIO_AUTH_TOKEN)

        call = client.calls.create(
            url=f"{settings.app.PUBLIC_HOST}/cold-calling/outgoing-call",
            to=to_phone_number,
            from_=settings.twilio.TWILIO_NUMBER,
        )
        return OutgoingParamsSchema(call_sid=call.sid)

    @staticmethod
    async def handle_outgoing_call(
        request: Request,
    ) -> HTMLResponse:  # TODO: maybe we will remove the logic with Twilio voice
        response = VoiceResponse()
        response.say("Please wait while we connect your call to the AI voice assistant...", voice=settings.twilio.TWILIO_VOICE)
        response.pause(length=1)
        response.say("O.K., now you and Aizen can talk to each other.", voice=settings.twilio.TWILIO_VOICE)
        connect = Connect()
        connect.stream(url=f"wss://{request.url.hostname}/cold-calling/media-stream")
        response.append(connect)
        return HTMLResponse(content=str(response), media_type="application/xml")

    async def validate_twilio_signature(self, request: Request) -> None:
        body = await request.body()

        if not settings.twilio.TWILIO_AUTH_TOKEN:
            self.log("[WARN] TWILIO_AUTH_TOKEN is not configured. Skipping signature validation.")
        else:
            ok = validate_twilio_signature(request, body, settings.twilio.TWILIO_AUTH_TOKEN)
            if not ok:
                self.log("[ERROR] Twilio signature validation failed.")
                raise HTTPException(status_code=403, detail="Forbidden")

    def get_caller_number(self, call_sid: str) -> None:
        call = self.client.calls(call_sid).fetch()
        self.caller_phone_number = call.from_formatted

        self.log(f"Caller phone number: {self.caller_phone_number}")

    async def handle_incoming_call(self, request: Request) -> HTMLResponse:
        await self.validate_twilio_signature(request=request)

        host = request.url.hostname
        response = VoiceResponse()
        connect = Connect()
        connect.stream(url=f"wss://{host}/ava/media-stream")
        response.append(connect)
        return HTMLResponse(content=str(response))

    async def handle_end_call(self, call_sid: str) -> None:
        await asyncio.to_thread(self.client.calls(call_sid).update, status="completed", method="POST")
        self.log(f"[TWILIO INFO] Finished CallSid={call_sid} successfully")

    async def redirect_to_manager(self, call_sid: str) -> None:
        transfer_url = f"{settings.app.PUBLIC_HOST}/ava/twilio/transfer"
        await asyncio.to_thread(self.client.calls(call_sid).update, url=transfer_url, method="POST")
        self.log(f"[TWILIO INFO] Redirected CallSid={call_sid} to {transfer_url}")

    @staticmethod
    def transfer_request() -> HTMLResponse:
        xml = f"""
            <Response>
              <Dial answerOnBridge="true" callerId="{settings.twilio.CALLER_ID}">
                <Number>{settings.twilio.REDIRECT_PHONE_NUMBER}</Number>
              </Dial>
            </Response>
            """.strip()
        return HTMLResponse(content=xml)
