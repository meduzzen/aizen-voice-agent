from enum import StrEnum
from pydantic import BaseModel, constr


class MsgType(StrEnum):
    USER = "user_message"
    START = "start"
    DELTA = "delta"
    END = "end"
    ERROR = "error"


class ClientMessage(BaseModel):
    type: MsgType = MsgType.USER
    text: constr(min_length=1, strip_whitespace=True)
