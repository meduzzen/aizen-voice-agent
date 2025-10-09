from pydantic import BaseModel


class InitMessageSchema(BaseModel):
    message: str
    