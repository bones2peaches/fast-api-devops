from pydantic import BaseModel, Field, root_validator
from typing import Optional, List, Literal, Union, get_type_hints
from datetime import datetime
import math
from typing_extensions import Annotated
import json
from enum import Enum
from typing import Optional
import uuid


class NotificationType(str, Enum):
    test = "test"
    message = "message"


class Test(BaseModel):

    type: Literal["test"] = "test"
    text: str = "this is a test event"
    created_at: Optional[datetime] = None


class Message(BaseModel):

    type: Literal["message"] = "message"
    user_id: uuid.UUID | str = Field(...)
    username: str = Field(...)
    chatroom_id: str = Field(...)
    chatroom_name: str = Field(...)


class Notification(BaseModel):
    event: Annotated[
        Union[Test, Message],
        Field(discriminator="type"),
    ] = Field(...)

    id: uuid.UUID | str = Field(...)
    read: Optional[bool] = False
    created_at: Optional[datetime] = None

    def hash_dict(self) -> dict:
        # Convert Notification fields to a dictionary with string values
        data = {
            "id": str(self.id),
            "read": str(self.read),
            "created_at": self.created_at.isoformat() if self.created_at else "",
        }

        for k, v in self.event.dict():
            data[k] = str(v)

        return data

    @root_validator
    def event_created_at(cls, values):
        if values["created_at"] is None:
            values["created_at"] = datetime.now()
        if values["read"] is None:
            values["read"] = False

        return values
