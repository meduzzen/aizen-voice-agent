from typing import Annotated

from fastapi import Depends

from app.core.dependencies.services import (
    KnowledgeBaseServiceDep,
    N8NServiceDep,
    TwilioServiceDep,
)
from app.services.tool_service import ToolService


async def get_tool_service(
    twilio_service: TwilioServiceDep,
    knowledge_base_service: KnowledgeBaseServiceDep,
    n8n_service: N8NServiceDep,
) -> ToolService:
    return ToolService(
        twilio_service=twilio_service,
        knowledge_base_service=knowledge_base_service,
        n8n_service=n8n_service,
        enabled_tools=["get_service_details"],
    )


ToolServiceDep = Annotated[ToolService, Depends(get_tool_service)]
