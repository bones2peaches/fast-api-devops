from fastapi import APIRouter, status, Depends, HTTPException, Response, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.user import Users, Sessions
from app.schema.user import UserIn, UserSchema, UserLogin, SessionToken
from app.schema.chatroom import ChatroomUsers
from app.schema.nchan import NchanEvent, NchanResponse, CountUpdate
from typing_extensions import Annotated
from app.services.auth import get_current_user
from app.services import metrics
from fastapi.responses import JSONResponse
import logging
from app.services.publisher import nchan_client

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED, response_model=UserSchema)
async def create_user(payload: UserIn, db: AsyncSession = Depends(get_db)):
    user = Users(username=payload.username, password=payload.hashed_password)
    await user.save(session=db)

    metrics.user_created_counter.inc()

    return UserSchema(username=user.username, id=user.id)


@router.post(
    "/session", status_code=status.HTTP_201_CREATED, response_model=SessionToken
)
async def create_session(
    payload: UserLogin, response: Response, db: AsyncSession = Depends(get_db)
):

    token = await Sessions.create(
        db_session=db, username=payload.username, password=payload.password
    )

    response.headers["Access-Control-Allow-Origin"] = "*"
    metrics.user_logged_in_counter.inc()
    response.set_cookie(
        key="session_token",
        value=token["token"]["access_token"],
        path="/",
        domain="localhost",
        secure=True,
        httponly=True,
        samesite="None",
    )

    response.set_cookie(
        key="username",
        value=payload.username,
        path="/",
        domain="localhost",
        secure=True,
        httponly=True,
        samesite="None",
    )
    response.set_cookie(
        key="user_id",
        value=token["id"],
        path="/",
        domain="localhost",
        secure=True,
        httponly=True,
        samesite="None",
    )

    response.set_cookie(
        key="expiry",
        value=token["token"]["expires"],
        path="/",
        domain="localhost",
        secure=True,
        httponly=True,
        samesite="None",
    )

    chatrooms = await token["user"].get_chatrooms_and_user_counts(db=db)

    event = NchanResponse(event="count_update", data={"chatrooms": chatrooms})
    publish = nchan_client.count_update(event=event)

    # for chatroom in chatrooms:
    #     event_data = await ChatroomUsers.query(chatroom_id=chatroom.id, session=db)
    #     event = NchanResponse(event="user", data=event_data)
    #     publish = nchan_client.publish_chatroom_users(
    #         chatroom_id=chatroom.id, event=event
    #     )
    return token["token"]


@router.delete("/session", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session: Annotated[Users, Depends(get_current_user)],
    response: Response,
    session_token: str = Cookie(None),
    db: AsyncSession = Depends(get_db),
):
    response.delete_cookie("username")
    response.delete_cookie("user_id")
    response.delete_cookie("session_token")

    token = await Sessions.delete(
        db_session=db, username=session.user.username, session_id=session.session_id
    )
    metrics.user_logged_out_counter.inc()

    chatrooms = await session.user.get_chatrooms_and_user_counts(db=db)
    # for chatroom in chatrooms:
    #     event_data = await ChatroomUsers.query(chatroom_id=chatroom.id, session=db)
    #     event = NchanResponse(event="user", data=event_data)
    #     publish = nchan_client.publish_chatroom_users(
    #         chatroom_id=chatroom.id, event=event
    #     )

    event = NchanResponse(event="count_update", data={"chatrooms": chatrooms})
    publish = nchan_client.count_update(event=event)
