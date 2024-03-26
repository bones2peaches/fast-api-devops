from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.user import Chatrooms, Users
from app.schema.chatroom import ChatroomIn, PaginatedChatroom, ChatroomOut, ChatroomUser
from typing_extensions import Annotated
from app.services.auth import get_current_user
from app.services import metrics
from app.exceptions import NotFoundHTTPException
import uuid

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ChatroomOut)
async def create_chatroom(
    session: Annotated[Users, Depends(get_current_user)],
    payload: ChatroomIn,
    db: AsyncSession = Depends(get_db),
):

    chatroom = Chatrooms(
        name=payload.name, category=payload.category, user_id=session.user.id
    )
    await chatroom.save(session=db)
    await db.refresh(chatroom)

    return ChatroomOut._return(chatroom=chatroom)


@router.get(
    "/{chatroom_id}", status_code=status.HTTP_200_OK, response_model=ChatroomOut
)
async def get_chatroom(
    chatroom_id: str | uuid.UUID,
    session: Annotated[Users, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):

    chatroom = await Chatrooms.find(db_session=db, name=chatroom_id, id=True)
    if chatroom is None:
        raise NotFoundHTTPException(msg=f"chatroom of id {chatroom_id} not found")
    else:
        return ChatroomOut._return(chatroom=chatroom)


@router.get("s", status_code=status.HTTP_200_OK, response_model=PaginatedChatroom)
async def list_chatrooms(
    page: int = 1,
    per_page: int = 5,
    db: AsyncSession = Depends(get_db),
):

    return await PaginatedChatroom.query(db_session=db, page=page, per_page=per_page)


