from pydantic import BaseModel, Field
from typing import Annotated, Literal
from app.schema.chatroom import ChatroomUsers, MessageOut, CountUpdate
from enum import Enum
from typing import Optional
from datetime import datetime


class NchanEvent(str, Enum):
    user_count = "user_count"
    count_update = "count_update"
    user_pull = "user_pull"
    message = "message"
    update = "update"


class NchanResponse(BaseModel):
    event: NchanEvent = Field(...)
    data: Optional[MessageOut | ChatroomUsers | CountUpdate] = None
    time: str = str(datetime.now())
