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


class UserIn(BaseModel):
    username: str = Field(...)
    hashed_password: str = Field(
        ..., validation_alias=AliasChoices("hashed_password", "password")
    )

    @field_validator("hashed_password")
    def password_length(cls, v):
        if len(v) < 7:
            raise BadRequestHTTPException(msg="Password needs to be at least 8 chars")
        return v

    @model_validator(mode="after")
    def gen_hashed_password(cls, values):
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        values.hashed_password = pwd_context.hash(values.hashed_password)
        return values


class SessionUser(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    user: Users
    session_id: str


class UserLogin(BaseModel):
    username: str = Field(...)
    password: str = Field(...)


class SessionToken(BaseModel):
    access_token: str
    expires: datetime


class UserSchema(BaseModel):
    username: str
    id: uuid.UUID


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
