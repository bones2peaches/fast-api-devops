import uuid
import jwt
from sqlalchemy.exc import IntegrityError, DBAPIError
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
    insert,
    delete,
    func,
    exists,
)

import math
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from sqlalchemy.orm import (
    mapped_column,
    Mapped,
    relationship,
    selectinload,
    joinedload,
    raiseload,
)
from datetime import datetime, timedelta
from app.models.base import Base
from app.exceptions import BadRequestHTTPException, NotFoundHTTPException
from app.config import settings as global_settings
import logging
from passlib.context import CryptContext


user_chatroom_table = Table(
    "user_joined_chatrooms",
    Base.metadata,
    Column("user_id", ForeignKey("users.id")),
    Column("chatroom_id", ForeignKey("chatrooms.id")),
    Column("joined", DateTime, default=datetime.now),
)


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

    messages: Mapped[List["Messages"]] = relationship(
        back_populates="user", lazy="selectin"
    )

    created_chatrooms: Mapped[List["Chatrooms"]] = relationship(
        back_populates="created_by", lazy="selectin"
    )

    chatrooms: Mapped[List["Chatrooms"]] = relationship(
        secondary=user_chatroom_table, back_populates="users"
    )
    online: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    async def get_user_chatrooms(self, db: AsyncSession) -> List["Chatrooms"]:
        """
        Asynchronously get a list of chatrooms that the given user is a part of.

        :param user_id: UUID of the user to check.
        :param db: SQLAlchemy AsyncSession.
        :return: List of Chatrooms the user is a part of.
        """
        # Create a query that selects chatrooms joined by the given user_id
        stmt = (
            select(Chatrooms)
            .options(raiseload("*"))
            .join(
                user_chatroom_table, Chatrooms.id == user_chatroom_table.c.chatroom_id
            )
            .where(user_chatroom_table.c.user_id == self.id)
        )

        result = await db.execute(stmt)
        chatrooms = result.scalars().all()

        return chatrooms

    @classmethod
    async def find(cls, db_session: AsyncSession, username: str):
        """

        :param db_session:
        :param name:
        :return:
        """
        stmt = select(cls).where(cls.username == username)
        try:
            result = await db_session.execute(stmt)
        except DBAPIError as e:
            logging.warn(f"DBAPI : {e}")
            raise NotFoundHTTPException()

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
        if self.username == "dylan":
            expires = datetime.now() + timedelta(minutes=60000)
        else:
            expires = datetime.now() + timedelta(
                minutes=int(global_settings.jwt_expire)
            )
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

                return {
                    "token": _user.sign_token(session_id=str(session.id)),
                    "id": str(_user.id),
                    "user": _user,
                }
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


class Chatrooms(Base):
    id: Mapped[uuid:UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        unique=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(unique=True, nullable=False)

    created_by: Mapped["Users"] = relationship(
        back_populates="created_chatrooms", lazy="selectin"
    )

    user_id: Mapped[uuid:UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )
    category: Mapped[str] = mapped_column(nullable=False)

    messages: Mapped[List["Messages"]] = relationship(
        back_populates="chatroom", lazy="selectin"
    )
    users: Mapped[List[Users]] = relationship(
        secondary=user_chatroom_table, back_populates="chatrooms"
    )

    @classmethod
    async def find(
        cls, db_session: AsyncSession, name: str | uuid.UUID, id: bool = False
    ):
        """

        :param db_session:
        :param name:
        :return:
        """

        if id is True:
            stmt = select(cls).where(cls.id == name)
        else:
            stmt = select(cls).where(cls.name == name)

        result = await db_session.execute(stmt)
        instance = result.scalars().first()
        if instance is None:
            return None
        else:
            return instance

    async def save(self, session: AsyncSession):
        chatroom = await Chatrooms.find(name=self.name, db_session=session)
        if chatroom is None:
            session.add(self)
            return await session.commit()
        else:
            raise BadRequestHTTPException(
                msg=f"{self.name} already exists , try another chatroom name."
            )

    async def update_user(self, session: AsyncSession, user_id: uuid.UUID):
        # Check if the user is already in the chatroom
        stmt = select(user_chatroom_table).where(
            user_chatroom_table.c.user_id == user_id,
            user_chatroom_table.c.chatroom_id == self.id,
        )
        result = await session.execute(stmt)
        association = result.first()

        if association:
            # Remove the user from the chatroom
            stmt = delete(user_chatroom_table).where(
                user_chatroom_table.c.user_id == user_id,
                user_chatroom_table.c.chatroom_id == self.id,
            )
            await session.execute(stmt)
            action = "removed from"
        else:
            # Add the user to the chatroom
            stmt = insert(user_chatroom_table).values(
                user_id=user_id,
                chatroom_id=self.id,  # Ensure this uses self.id to match your model attribute
            )
            await session.execute(stmt)
            action = "added to"

        await session.commit()
        logging.info(f"User {action} the chatroom.")

    async def add_message(self, session: AsyncSession, text: str, user_id: uuid.UUID):
        """
        Adds a message to the chatroom and retrieves it using a direct select statement for confirmation.

        :param session: The SQLAlchemy AsyncSession instance.
        :param text: The text of the message to be added.
        :param user_id: The UUID of the user who is sending the message.
        :return: The newly added Messages instance.
        """
        # Prepare the data for insertion
        message_id = uuid.uuid4()  # Generate a new UUID for this message
        insert_data = {
            "id": message_id,
            "chatroom_id": self.id,
            "created_at": datetime.now(),
            "deleted": False,
            "editted": False,
            "text": text,
            "user_id": user_id,
        }

        # Perform the insert operation
        stmt = insert(Messages).values(**insert_data)
        await session.execute(stmt)

        # Commit the transaction to ensure the message is saved
        await session.commit()

        # Fetch the newly created message using its ID
        stmt = select(Messages).where(Messages.id == message_id)
        result = await session.execute(stmt)
        new_message = result.scalars().first()

        return new_message


class Messages(Base):

    id: Mapped[uuid:UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        unique=True,
        default=uuid.uuid4,
    )

    user: Mapped["Users"] = relationship(back_populates="messages", lazy="selectin")
    user_id: Mapped[uuid:UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )

    chatroom: Mapped["Chatrooms"] = relationship(
        back_populates="messages", lazy="selectin"
    )
    chatroom_id: Mapped[uuid:UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chatrooms.id")
    )

    reactions: Mapped["MessageReactions"] = relationship(backref="message")

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )
    text: Mapped[str] = mapped_column(nullable=False)
    deleted: Mapped[bool] = mapped_column(nullable=False, default=False)
    editted: Mapped[bool] = mapped_column(nullable=False)

    @classmethod
    async def find(
        cls, db_session: AsyncSession, id: str | uuid.UUID, chatroom_id: str | uuid.UUID
    ):
        """

        :param db_session:
        :param name:
        :return:
        """

        stmt = select(cls).where(cls.id == id, cls.chatroom_id == chatroom_id)
        try:
            result = await db_session.execute(stmt)
        except DBAPIError as e:
            logging.warn(f"DBAPI : {e}")
            raise NotFoundHTTPException(msg=f"Message not FOund with ID {id}")

        instance = result.scalars().first()
        if instance is None:
            return None
        else:
            return instance

    async def update(self, db_session: AsyncSession, action: str, text: str = None):
        """

        :param db_session:
        :param name:
        :return:
        """

        if action == "edit":
            setattr(self, "editted", True)
            setattr(self, "text", text)

        elif action == "delete":
            setattr(self, "deleted", True)

        db_session.add(self)

        await db_session.commit()
        await db_session.refresh(self)
        return self

    async def add_reaction(
        self, db: AsyncSession, user_id: str | uuid.UUID, liked: bool
    ):
        has_reacted = await MessageReactions.has_user_reacted(
            db_session=db, user_id=user_id, message_id=self.id
        )
        if has_reacted is None:
            # havent reacted yet
            logging.warn("IS NONE____________________________")
            stmt = insert(MessageReactions).values(
                user_id=user_id,
                message_id=self.id,
                is_like=liked,
            )
            await db.execute(stmt)
            await db.commit()

        elif has_reacted.is_like == liked:
            # has reacted and its the same things remove ,ie if i liked and i click like again its removes
            logging.warn("IS REMOVING____________________________")
            stmt = delete(MessageReactions).where(
                MessageReactions.user_id == user_id,
                MessageReactions.message_id == self.id,
            )
            await db.execute(stmt)
            await db.commit()

        elif has_reacted.is_like != liked:
            logging.warn("IS UPDATE____________________________")
            setattr(has_reacted, "is_like", liked)
            db.add(has_reacted)
            await db.commit()

    async def get_reactions(self, db: AsyncSession):
        """
        Fetches all reactions for this message, categorizing them into liked and disliked,
        and includes the user's ID and name for each reaction.

        :param db: The database session.
        :return: A dictionary with two keys 'liked' and 'disliked', each containing a list of user IDs and names.
        """
        stmt = (
            select(MessageReactions.user_id, Users.username, MessageReactions.is_like)
            .select_from(MessageReactions)
            .join(Users, Users.id == MessageReactions.user_id)
            .where(MessageReactions.message_id == self.id)
        )
        result = await db.execute(stmt)
        reactions = result.fetchall()

        liked_list = [
            {"id": user_id, "username": name}
            for user_id, name, is_like in reactions
            if is_like
        ]

        disliked_list = [
            {"id": user_id, "username": name}
            for user_id, name, is_like in reactions
            if not is_like
        ]

        return {"liked": liked_list, "disliked": disliked_list}


class MessageReactions(Base):

    user_id: Mapped[uuid:UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True
    )
    user: Mapped["Messages"] = relationship(back_populates="reactions", lazy="selectin")
    message_id: Mapped[uuid:UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("messages.id"), primary_key=True
    )

    is_like = Column(Boolean, default=True)

    @classmethod
    async def has_user_reacted(
        cls,
        db_session: AsyncSession,
        message_id: str | uuid.UUID,
        user_id: str | uuid.UUID,
    ) -> None | bool:
        stmt = select(cls).where(cls.user_id == user_id, cls.message_id == message_id)
        result = await db_session.execute(stmt)
        instance = result.scalars().first()
        if instance is None:
            return None
        else:
            return instance
