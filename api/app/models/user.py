import uuid
import jwt
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import backref
from sqlalchemy import (
    String,
    DateTime,
    select,
    ForeignKey,
    Boolean,
    Table,
    Column,
    Enum,
    JSON,
    update,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from sqlalchemy.orm import mapped_column, Mapped, relationship
from datetime import datetime, timedelta
from app.models.base import Base
from app.exceptions import BadRequestHTTPException
from app.config import settings as global_settings
import logging
from passlib.context import CryptContext


class Users(Base):

    id: Mapped[uuid:UUID] = mapped_column(
        UUID(as_uuid=True), unique=True, default=uuid.uuid4, autoincrement=True
    )
    username: Mapped[str] = mapped_column(String, primary_key=True, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )

    sessions: Mapped[List["Sessions"]] = relationship(
        back_populates="user", lazy="selectin"
    )
    online: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    @classmethod
    async def find(cls, db_session: AsyncSession, username: str):
        """

        :param db_session:
        :param name:
        :return:
        """
        stmt = select(cls).where(cls.username == username)
        result = await db_session.execute(stmt)
        instance = result.scalars().first()
        if instance is None:
            return None
        else:
            return instance

    async def save(self, session: AsyncSession):
        _user = await Users.find(username=self.username, db_session=session)
        if _user is None:
            session.add(self)
            return await session.commit()
        else:
            raise BadRequestHTTPException(
                msg=f"{self.username} already exists , try another username."
            )

    def sign_token(self, session_id: str) -> str:
        expires = datetime.now() + timedelta(minutes=int(global_settings.jwt_expire))
        data = {
            "username": self.username,
            "session_id": str(session_id),
            # Use the 'exp' claim for expiration, and convert the datetime to a Unix timestamp
            "exp": expires.timestamp(),
            "id": str(self.id),
        }
        token = jwt.encode(
            data, global_settings.jwt_key, algorithm=global_settings.jwt_algorithm
        )

        return dict(expires=expires, access_token=token)


class Sessions(Base):
    id: Mapped[uuid:UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        unique=True,
        default=uuid.uuid4,
    )

    user: Mapped["Users"] = relationship(back_populates="sessions", lazy="selectin")
    user_id: Mapped[uuid:UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )
    logout: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    @classmethod
    async def find(cls, db_session: AsyncSession, id: uuid.UUID):
        """

        :param db_session:
        :param name:
        :return:
        """
        stmt = select(cls).where(cls.id == id)
        result = await db_session.execute(stmt)
        instance = result.scalars().first()
        if instance is None:
            return None
        else:
            return instance

    @classmethod
    async def create(cls, db_session, username, password):
        _user = await Users.find(username=username, db_session=db_session)

        if _user is None:
            raise BadRequestHTTPException(msg="incorrect username or password")

        else:
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            check = pwd_context.verify(password, _user.password)
            if check:
                session = cls(user_id=_user.id)
                db_session.add(session)
                setattr(_user, "online", True)
                db_session.add(_user)
                await db_session.commit()

                return _user.sign_token(session_id=str(session.id))
            else:
                raise BadRequestHTTPException(msg="incorrect username or password")

    @classmethod
    async def delete(cls, db_session, username, session_id):
        _session = await Sessions.find(db_session=db_session, id=uuid.UUID(session_id))

        user = await Users.find(username=username, db_session=db_session)

        setattr(user, "online", False)
        setattr(_session, "logout", datetime.now())
        db_session.add(_session)
        db_session.add(user)
        await db_session.commit()
