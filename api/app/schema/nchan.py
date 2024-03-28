from pydantic import BaseModel, Field
from typing import Annotated, Literal
from app.schema.chatroom import ChatroomUsers, MessageOut
from enum import Enum
from typing import Optional


class NchanEvent(str, Enum):
    user = "user"
    user_pull = "user_pull"
    message = "message"
    update = "update"


class NchanResponse(BaseModel):
    event: NchanEvent = Field(...)
    data: Optional[MessageOut | ChatroomUsers] = None
