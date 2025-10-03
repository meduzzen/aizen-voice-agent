from typing import Any

import httpx

from app.core.mixins import LogMixin
from app.integrations.base import ChatIntegration, ConversationSummary


class TeamsIntegration(ChatIntegration, LogMixin):
    def __init__(self, webhook_url: str, version: str = "1.5") -> None:
        self.webhook_url = webhook_url
        self.version = version

    @staticmethod
    def _format_title_text(data: ConversationSummary) -> tuple[str, str]:
        title = f"Conversation with a client {data.phone_number or '<unknown>'}"
        text = f"name: {data.client_name or 'unknown'}\n" f"summary: {data.summary or 'no summary available'}"
        return title, text

    async def send_summary(self, data: ConversationSummary) -> None:
        if not self.webhook_url:
            self.log("[TEAMS][WARN] WEBHOOK_URL is empty. Skipping message.")
            return

        title, text = self._format_title_text(data)

        adaptive_card: dict[str, Any] = {
            "$schema": "https://adaptivecards.io/schemas/adaptive-card.json",
            "type": "AdaptiveCard",
            "version": self.version,
            "body": [
                {"type": "TextBlock", "size": "Large", "weight": "Bolder", "wrap": True, "text": title},
                {"type": "TextBlock", "wrap": True, "text": text},
            ],
        }

        payload: dict[str, Any] = {
            "type": "message",
            "attachments": [{"contentType": "application/vnd.microsoft.card.adaptive", "contentUrl": None, "content": adaptive_card}],
        }

        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(self.webhook_url, json=payload)
            try:
                r.raise_for_status()
            except httpx.HTTPStatusError as e:
                self.log(f"[TEAMS][ERROR] POST failed: {e.response.status_code} {e.response.text}")
                raise
            else:
                self.log("[TEAMS][OK] Adaptive Card sent.")
