from typing import Annotated

from fastapi import Depends

from app.core.dependencies.services import KnowledgeBaseServiceDep, TwilioServiceDep
from app.services.tool_service import ToolService


async def get_tool_service(
    twilio_service: TwilioServiceDep,
    knowledge_base_service: KnowledgeBaseServiceDep,
) -> ToolService:
    return ToolService(
        twilio_service=twilio_service,
        knowledge_base_service=knowledge_base_service,
        enabled_tools=["get_service_details"],
    )


ToolServiceDep = Annotated[ToolService, Depends(get_tool_service)]
