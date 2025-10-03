from app.core.config.config import settings
from app.schemas.messenger import PostSummaryOptions
from app.services.integrations.base import ChatIntegration
from app.services.integrations.outlook import OutlookIntegration
from app.services.integrations.teams import TeamsIntegration


class IntegrationRegistry:
    _cache: dict[str, ChatIntegration] = {}

    @classmethod
    def get(cls, name: PostSummaryOptions | str) -> ChatIntegration:
        key = name.value if isinstance(name, PostSummaryOptions) else str(name)
        key = key.lower()

        if key in cls._cache:
            return cls._cache[key]
        if key == PostSummaryOptions.teams.value:
            inst = TeamsIntegration(webhook_url=settings.teams.WEBHOOK_URL)
        elif key == PostSummaryOptions.outlook.value:
            inst = OutlookIntegration()
        else:
            raise KeyError(f"Unknown integration: {name}")
        cls._cache[key] = inst
        return inst
