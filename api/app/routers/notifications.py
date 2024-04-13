from fastapi import APIRouter, status, Depends, HTTPException, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.user import Chatrooms, Users, Notifications


from typing_extensions import Annotated
from app.services.auth import get_current_user, get_cookie_user
import uuid
from datetime import datetime
from app.exceptions import BadRequestHTTPException
from app.schema.notifications import (
    NotificationMessage,
    Notification,
    NotificationType,
    PaginatedNotificatons,
)
import logging
from app.services.publisher import nchan_client

router = APIRouter()


@router.put(
    "/{notification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def update_notifications(
    notification_id: str | uuid.UUID,
    session: Annotated[Users, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):

    await Notifications.update(db=db, id=notification_id, user_id=session.user.id)


@router.get("", status_code=status.HTTP_200_OK, response_model=PaginatedNotificatons)
async def list_unread_notifications(
    session: Annotated[Users, Depends(get_current_user)],
    page: int = 1,
    per_page: int = 5,
    db: AsyncSession = Depends(get_db),
):

    return await Notifications.query(
        db_session=db, page=page, per_page=per_page, user=session.user
    )
