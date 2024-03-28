from fastapi import Depends, Query, Cookie
from app.utils.logging import AppLogger


from fastapi.security import OAuth2PasswordBearer
from typing_extensions import Annotated
import jwt
from app.schema.user import SessionUser
from app.models.user import Users
from app.exceptions import AuthTokenExpiredHTTPException, AuthFailedHTTPException
from app.config import settings as global_settings
import os

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/user/session")


def decode_token(
    token: str,
) -> SessionUser:
    try:
        payload = jwt.decode(
            token, global_settings.jwt_key, algorithms=[global_settings.jwt_algorithm]
        )
    except jwt.ExpiredSignatureError:
        raise AuthTokenExpiredHTTPException()

    user_id = payload.get("id")
    session_id = payload.get("session_id")
    username = payload.get("username")
    if user_id is None or session_id is None or username is None:
        raise AuthFailedHTTPException()

    user_data = Users(
        id=user_id,
        username=username,
        password="",
    )

    return SessionUser(user=user_data, session_id=session_id)


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    if token is None:
        raise AuthFailedHTTPException()

    try:
        user = decode_token(token)
    except jwt.DecodeError:
        raise AuthFailedHTTPException()
    return user


async def get_event_current_user(token: str = Query(..., alias="access_token")):
    if token is None:
        raise AuthFailedHTTPException()

    try:
        user = decode_token(token)
    except jwt.DecodeError:
        raise AuthFailedHTTPException()
    return user


async def get_cookie_user(
    session_token: str = Cookie(None),
):
    token = session_token
    if token is None:
        raise AuthFailedHTTPException()

    try:
        user = decode_token(token)
    except jwt.DecodeError:
        raise AuthFailedHTTPException()
    return user
