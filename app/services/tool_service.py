from typing import Callable

from langchain_openai import ChatOpenAI

from app.core import settings
from app.core.mixins import LogMixin
from app.schemas.service import ServiceData
from app.services.knowledge_base import KnowledgeBaseService
from app.services.n8n import N8NService
from app.services.twilio_service import TwilioService


class ToolService(LogMixin):
    def __init__(
        self,
        twilio_service: TwilioService,
        knowledge_base_service: KnowledgeBaseService,
        n8n_service: N8NService,
        enabled_tools: list[str] | None = None,
    ) -> None:
        self.llm = ChatOpenAI(api_key=settings.open_ai.OPENAI_API_KEY, model=settings.open_ai.CHAT_MODEL)
        self.twilio_service = twilio_service
        self.knowledge_base_service = knowledge_base_service
        self.n8n_service = n8n_service
        self.enabled_tools = enabled_tools or [
            "get_service_details",
            "finish_the_call",
            "send_client_form",
            "redirect_to_manager",
        ]

    @property
    def tool_mapping(self) -> dict[str, Callable]:
        mapping = {
            "get_service_details": self.get_service_details,
            "finish_the_call": self.finish_the_call,
            "send_client_form": self.send_client_form,
            "redirect_to_manager": self.redirect_to_manager,
        }
        return {k: v for k, v in mapping.items() if k in self.enabled_tools}

    async def get_service_details(self, query: str, *args, **kwargs) -> str:
        return await self.knowledge_base_service.retrieve(query)

    async def finish_the_call(self, call_sid: str, *args, **kwargs) -> None:
        return await self.twilio_service.handle_end_call(call_sid=call_sid)

    async def redirect_to_manager(self, call_sid: str, *args, **kwargs) -> None:
        return await self.twilio_service.redirect_to_manager(call_sid=call_sid)

    async def send_client_form(
        self,
        trust_account_name: str,
        bsb: str,
        account_number: str,
        phone_number: str,
        email: str,
        first_name: str,
        last_name: str,
        matter_type: str,
        matter_jurisdiction: str,
        *args,
        **kwargs,
    ) -> str | None:
        service_data = await self.knowledge_base_service.retrieve(
            query=f"get the price, disbursements and description of the service provided {matter_type}"
        )
        prompt = f"""
            You are a data extractor. From the following context, extract the service details.
            Respond ONLY in valid JSON that matches this schema:
            {{
                "fee_estimate": "float",
                "disbursement_estimate": "float",
                "service_description": "string"
            }}

            Context:
            {service_data}
            """
        response = await self.llm.with_structured_output(ServiceData).ainvoke(prompt)
        self.log(f"[DEBUG] Extracted service data: {response}")
        return await self.n8n_service.trigger_n8n_workflow(
            fee_estimate=response.fee_estimate,
            disbursement_estimate=response.disbursement_estimate,
            initial_trust_amount=response.fee_estimate + response.disbursement_estimate,
            trust_account_name=trust_account_name,
            bsb=bsb,
            account_number=account_number,
            phone=phone_number,
            email=email,
            first_name=first_name,
            last_name=last_name,
            matter_type=matter_type,
            matter_jurisdiction=matter_jurisdiction,
            service_description=response.service_description,
        )
