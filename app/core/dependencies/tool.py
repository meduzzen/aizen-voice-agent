from typing import Annotated

from fastapi import Depends

from app.core.dependencies.services import (
    GHLServiceDep,
    KnowledgeBaseServiceDep,
    TwilioServiceDep,
)
from app.services.tool_service import ToolService


async def get_web_bot_tool_service(
    twilio_service: TwilioServiceDep,
    knowledge_base_service: KnowledgeBaseServiceDep,
    gohighlevel_service: GHLServiceDep,
) -> ToolService:
    return ToolService(
        twilio_service=twilio_service,
        knowledge_base_service=knowledge_base_service,
        gohighlevel_service=gohighlevel_service,
        enabled_tools=[
            "get_service_details",
            "create_contact",
            "update_contact_info",
            "get_free_appointment_slots",
            "create_appointment",
            "wait_for",
            "get_phone_number",
        ],
    )


async def get_cold_calling_tool_service(
    twilio_service: TwilioServiceDep,
    knowledge_base_service: KnowledgeBaseServiceDep,
    gohighlevel_service: GHLServiceDep,
) -> ToolService:
    return ToolService(
        twilio_service=twilio_service,
        knowledge_base_service=knowledge_base_service,
        gohighlevel_service=gohighlevel_service,
        enabled_tools=["get_service_details"],
    )


ToolServiceSalesDep = Annotated[ToolService, Depends(get_web_bot_tool_service)]
ToolServiceColdCallingDep = Annotated[ToolService, Depends(get_cold_calling_tool_service)]
