from pydantic import BaseModel, Field


class ServiceData(BaseModel):
    fee_estimate: float = Field(..., description="The fixed price of the service")
    disbursement_estimate: float | None = Field(default=0.0, description="The disbursements for the service if provided")
    service_description: str
