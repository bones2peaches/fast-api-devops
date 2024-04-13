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


class NotificationMessage(BaseModel):

    type: Literal["message"] = "message"
    user_id: uuid.UUID | str = Field(...)
    username: str = Field(...)
    chatroom_id: str = Field(...)
    chatroom_name: str = Field(...)

    def event_text(self):
        return f"{self.username} has seen a message in the chatroom called {self.chatroom_name}!"


class Notification(BaseModel):
    event: Annotated[
        Union[Test, NotificationMessage],
        Field(discriminator="type"),
    ] = Field(...)

    id: uuid.UUID | str = Field(...)
    read: Optional[bool] = False
    created_at: Optional[datetime] = datetime.now()

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


class NotificationOut(BaseModel):
    type: str
    text: str
    id: uuid.UUID
    user_id: uuid.UUID
    chatroom_id: uuid.UUID
    created_at: datetime
    read: bool = False


class PaginatedNotificatons(BaseModel):
    current_page: int = Field(...)
    total_pages: int = Field(...)
    total_items: int = Field(...)
    per_page: int = Field(...)
    items: List[NotificationOut] = Field(...)
