from abc import ABC, abstractmethod

from app.schemas.summary import SummarySchema


class ChatIntegration(ABC):
    """Base interface for chat integrations."""

    @abstractmethod
    async def send_summary(self, data: SummarySchema) -> None:
        """Send a conversation summary to the target chat."""
        raise NotImplementedError
