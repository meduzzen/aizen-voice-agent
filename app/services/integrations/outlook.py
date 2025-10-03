import time
from typing import Any

import httpx
import msal

from app.core import settings
from app.core.mixins import LogMixin
from app.schemas.summary import SummarySchema
from app.services.integrations.base import ChatIntegration


class OutlookIntegration(ChatIntegration, LogMixin):
    def __init__(self) -> None:
        cfg = settings.outlook
        self.graph_base = cfg.GRAPH_BASE.rstrip("/")
        self.sender_upn = cfg.SENDER_UPN
        self.scope = [cfg.SCOPE]
        self._app = msal.ConfidentialClientApplication(
            cfg.CLIENT_ID,
            authority=cfg.authority(),
            client_credential=cfg.CLIENT_SECRET,
        )
        self._cached_token: dict[str, Any] | None = None
        self._cached_exp: float = 0.0

    async def _get_token(self) -> str:
        now = time.time()
        if self._cached_token and now < self._cached_exp - 60:
            return self._cached_token["access_token"]

        result = self._app.acquire_token_silent(scopes=self.scope, account=None)
        if not result:
            result = self._app.acquire_token_for_client(scopes=self.scope)

        if "access_token" not in result:
            self.log(f"[OUTLOOK][ERROR] Token acquisition failed: {result}")
            raise RuntimeError("Failed to acquire Graph token")

        self._cached_token = result
        self._cached_exp = now + float(result.get("expires_in", 3600))
        return result["access_token"]

    @staticmethod
    def _format_mail(data: SummarySchema) -> tuple[str, str]:
        subject = f"Call summary: {data.phone_number or '<unknown>'}"
        body_lines = [
            f"Client name: {data.client_name or 'unknown'}",
            "",
            "Summary:",
            data.conversation_summary or "no summary available",
        ]
        body_text = "\n".join(body_lines)
        return subject, body_text

    async def send_summary(self, data: SummarySchema) -> None:
        if not self.sender_upn:
            self.log("[OUTLOOK][WARN] SENDER_UPN is empty. Skipping email.")
            return

        token = await self._get_token()
        subject, body_text = self._format_mail(data)

        payload: dict[str, Any] = {
            "message": {
                "subject": subject,
                "body": {"contentType": "Text", "content": body_text},
                "toRecipients": [{"emailAddress": {"address": self.sender_upn}}],
            },
            "saveToSentItems": True,
        }

        url = f"{self.graph_base}/users/{self.sender_upn}/sendMail"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post(url, headers=headers, json=payload)
            if r.status_code >= 400:
                self.log(f"[OUTLOOK][ERROR] POST failed: {r.status_code} {r.text}")
                r.raise_for_status()
            else:
                self.log("[OUTLOOK][OK] sendMail accepted.")
