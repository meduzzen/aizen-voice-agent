from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(slots=True)
class ConversationSummary:
    phone_number: str | None
    client_name: str | None
    summary: str


class ChatIntegration(ABC):
    """Base interface for chat integrations."""

    @abstractmethod
    async def send_summary(self, data: ConversationSummary) -> None:
        """Send a conversation summary to the target chat."""
        raise NotImplementedError
