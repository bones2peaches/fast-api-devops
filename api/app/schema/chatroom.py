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
from app.models.user import Chatrooms, Users
from app.exceptions import BadRequestHTTPException
import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy import func
import math
from enum import Enum


class ChatroomIn(BaseModel):
    name: str = Field(...)
    category: str = Field(...)


class ChatroomUser(BaseModel):
    username: str = Field(...)
    id: str | uuid.UUID = Field(...)
    online: Optional[bool] = None


class ChatroomUsers(BaseModel):
    users: List[ChatroomUser] = Field(...)

    @classmethod
    async def query(cls, chatroom_id: uuid.UUID, session: AsyncSession):
        result = await session.execute(
            select(Chatrooms)
            .options(joinedload(Chatrooms.users))
            .where(Chatrooms.id == chatroom_id)
        )
        chatroom = result.scalars().first()

        if not chatroom:
            return cls(users=[])

        return cls(
            users=[
                ChatroomUser(
                    username=user.username, id=str(user.id), online=user.online
                )
                for user in chatroom.users
            ]
        )


class MessageOut(BaseModel):
    text: str = Field(...)
    sent: datetime = Field(...)
    likes: List[ChatroomUser] = Field(...)
    dislikes: List[ChatroomUser] = Field(...)
    sent_by: ChatroomUser = Field(...)
    id: uuid.UUID = Field(...)
    editted: bool = Field(...)
    deleted: bool = Field(...)


class MessageIn(BaseModel):
    text: str = Field(...)


class ChatRoomMessages(BaseModel):
    messages: List[MessageOut] = Field(...)


class ChatroomOut(BaseModel):
    id: uuid.UUID = Field(...)
    name: str = Field(...)
    category: str = Field(...)
    created_at: datetime = Field(...)
    created_by: ChatroomUser = Field(...)

    @classmethod
    def _return(cls, chatroom: Chatrooms):
        return cls(
            name=chatroom.name,
            category=chatroom.category,
            created_at=chatroom.created_at,
            created_by=ChatroomUser(
                id=chatroom.created_by.id,
                username=chatroom.created_by.username,
                online=chatroom.created_by.online,
            ),
            id=chatroom.id,
        )


class PaginatedChatroom(BaseModel):
    current_page: int = Field(...)
    total_pages: int = Field(...)
    total_items: int = Field(...)
    per_page: int = Field(...)
    items: List[ChatroomOut] = Field(...)

    @classmethod
    async def query(
        cls,
        db_session: AsyncSession,
        page: int,
        per_page: int,
    ):
        base_query = select(Chatrooms).order_by(Chatrooms.created_at.desc())

        count_stmt = select(func.count()).select_from(base_query.subquery())
        total_items_result = await db_session.execute(count_stmt)
        total_items = total_items_result.scalar_one()

        total_pages = math.ceil(total_items / per_page)
        offset = (page - 1) * per_page

        # Apply pagination to the base query
        final_stmt = base_query.offset(offset).limit(per_page)
        users_result = await db_session.execute(final_stmt)
        chatrooms_db = users_result.scalars().all()

        items = []

        for chatroom in chatrooms_db:
            items.append(ChatroomOut._return(chatroom=chatroom))

        return cls(
            current_page=page,
            total_pages=total_pages,
            total_items=total_items,
            per_page=per_page,
            items=items,
        )


class MessageUpdateEnum(str, Enum):
    edit = "edit"
    delete = "delete"
    reaction = "reaction"


class UpdateMessage(BaseModel):
    action: MessageUpdateEnum = Field(...)
    message_id: str | uuid.UUID = Field(...)
    text: Optional[str] = None
    liked: Optional[bool] = None

    class Config:
        use_enum_values = True

    @model_validator(mode="after")
    def update_check(cls, values):
        if values.action == "edit" and values.text == None:
            raise BadRequestHTTPException(
                "if action is edit , the value for text cannot be None."
            )

        elif values.action == "reaction" and values.liked == None:

            raise BadRequestHTTPException(
                "if action is reaction , the value for liked cannot be None."
            )
        else:
            return values