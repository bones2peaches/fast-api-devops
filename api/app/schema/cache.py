from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
    AliasChoices,
    ConfigDict,
)
from passlib.context import CryptContext
from datetime import datetime
from app.models.user import Users
from app.exceptions import BadRequestHTTPException
import uuid
from typing import List


class RecentChatroom(BaseModel):
    id: uuid.UUID = Field(...)
    name: str = Field(...)
    category: str = Field(...)
    message_id: str = Field(...)
    message_text: str = Field(...)
    username: str = Field(...)
    user_id: str = Field(...)


class ViewUser(BaseModel):
    id: uuid.UUID = Field(...)
