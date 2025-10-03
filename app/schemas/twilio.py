from pydantic import BaseModel


class OutgoingParamsSchema(BaseModel):
    call_sid: str
