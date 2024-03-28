from fastapi import APIRouter, status, Depends, HTTPException, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.user import Chatrooms, Users, Messages, MessageReactions
from app.schema.chatroom import (
    ChatroomIn,
    ChatroomOut,
    ChatroomUser,
    MessageOut,
    MessageIn,
    ChatroomUsers,
    UpdateMessage,
)

from app.schema.nchan import NchanResponse
from typing_extensions import Annotated
from app.services.auth import get_event_current_user, get_current_user, get_cookie_user
from app.services import metrics
import uuid
from datetime import datetime
from app.exceptions import BadRequestHTTPException
import logging

router = APIRouter()


@router.get("/subscribe", status_code=status.HTTP_204_NO_CONTENT)
async def nchan_subscribe():
    metrics.ws_connection_counter.inc()


@router.get("/unsubscribe", status_code=status.HTTP_204_NO_CONTENT)
async def nchan_subscribe():
    metrics.ws_disconnection_counter.inc()


@router.get("/auth", status_code=status.HTTP_204_NO_CONTENT)
async def nchan_auth(
    request: Request,
    session: Annotated[Users, Depends(get_cookie_user)],
):

    logging.warn(f"COOKIES : {request.cookies}")
    return ""


@router.post(
    "/chatroom/{chatroom_id}/user",
    status_code=status.HTTP_201_CREATED,
    response_model=NchanResponse,
)
async def nchan_user_join(
    chatroom_id: str | uuid.UUID,
    session: Annotated[Users, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):

    chatroom = await Chatrooms.find(db_session=db, id=True, name=chatroom_id)
    await chatroom.update_user(session=db, user_id=session.user.id)

    data = await ChatroomUsers.query(chatroom_id=chatroom.id, session=db)
    return NchanResponse(event="user", data=data)


@router.post(
    "/chatroom/{chatroom_id}/message",
    status_code=status.HTTP_201_CREATED,
    response_model=NchanResponse,
)
async def nchan_send_message(
    chatroom_id: str | uuid.UUID,
    payload: MessageIn,
    session: Annotated[Users, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):

    chatroom = await Chatrooms.find(db_session=db, id=True, name=chatroom_id)
    message = await chatroom.add_message(
        session=db, text=payload.text, user_id=session.user.id
    )

    data = MessageOut(
        text=payload.text,
        sent=datetime.now(),
        likes=[],
        dislikes=[],
        sent_by=ChatroomUser(username=session.user.username, id=session.user.id),
        id=message.id,
        editted=False,
        deleted=False,
    )

    return NchanResponse(event="message", data=data)


@router.post(
    "/chatroom/{chatroom_id}/update",
    status_code=status.HTTP_201_CREATED,
    response_model=NchanResponse,
)
async def nchan_update_message(
    chatroom_id: str | uuid.UUID,
    payload: UpdateMessage,
    session: Annotated[Users, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):

    message = await Messages.find(
        db_session=db, id=payload.message_id, chatroom_id=chatroom_id
    )

    if payload.action in ["edit", "delete"]:
        check = str(message.user_id) == str(session.user.id)

        if check is False:
            raise BadRequestHTTPException(
                msg=f"{str(session.user.id)} did not send this message and cannot edit or delete it."
            )

        else:
            message = await message.update(
                db_session=db, action=payload.action, text=payload.text
            )

    else:

        update_reaction = await message.add_reaction(
            db=db, user_id=session.user.id, liked=payload.liked
        )

    reactions = await message.get_reactions(db=db)

    data = MessageOut(
        text=message.text,
        sent=message.created_at,
        likes=reactions["liked"],
        dislikes=reactions["disliked"],
        sent_by=ChatroomUser(username=session.user.username, id=session.user.id),
        id=message.id,
        editted=message.editted,
        deleted=message.deleted,
    )

    return NchanResponse(event="update", data=data)
