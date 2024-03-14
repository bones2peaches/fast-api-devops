from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.user import Users, Sessions
from app.schema.user import UserIn, UserSchema, UserLogin, SessionToken
from typing_extensions import Annotated
from app.services.auth import get_current_user
from app.services import metrics

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
async def create_session(payload: UserLogin, db: AsyncSession = Depends(get_db)):

    token = await Sessions.create(
        db_session=db, username=payload.username, password=payload.password
    )

    metrics.user_logged_in_counter.inc()

    return token


@router.delete("/session", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session: Annotated[Users, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):

    token = await Sessions.delete(
        db_session=db, username=session.user.username, session_id=session.session_id
    )
    metrics.user_logged_out_counter.inc()
