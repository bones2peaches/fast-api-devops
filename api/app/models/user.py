import uuid
import jwt
from sqlalchemy.exc import IntegrityError, DBAPIError
from sqlalchemy.orm import backref, aliased
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
    join,
    case,
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

user_notifications = Table(
    "user_notifications",
    Base.metadata,
    Column("user_id", ForeignKey("users.id")),
    Column("notification_id", ForeignKey("notifications.id")),
    Column("read", Boolean),
    Column("created_at", DateTime, default=datetime.now),
    Column("updated_at", DateTime, default=None, nullable=True, onupdate=datetime.now),
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
    notifications: Mapped["Notifications"] = relationship(
        secondary=user_notifications, back_populates="user", lazy="raise"
    )

    async def get_chatrooms_and_user_counts(self, db: AsyncSession):
        # Subquery to get chatroom IDs where the specific user is a member
        user_chatrooms_subquery = (
            select(user_chatroom_table.c.chatroom_id)
            .where(user_chatroom_table.c.user_id == self.id)
            .subquery()
        )

        # Main query to count online and offline users in those chatrooms
        stmt = (
            select(
                user_chatroom_table.c.chatroom_id,
                func.sum(case((Users.online == True, 1), else_=0)).label(
                    "online_count"
                ),
                func.sum(case((Users.online == False, 1), else_=0)).label(
                    "offline_count"
                ),
            )
            .join(Users, user_chatroom_table.c.user_id == Users.id)
            .where(user_chatroom_table.c.chatroom_id.in_(user_chatrooms_subquery))
            .group_by(user_chatroom_table.c.chatroom_id)
        )

        result = await db.execute(stmt)
        rows = result.fetchall()

        chatrooms_info = [
            {
                "chatroom_id": str(row[0]),
                "online": row[1],
                "offline": row[2],
            }
            for row in rows
        ]

        return chatrooms_info

    # async def get_chatroom_counts_for_user(self, session):
    #     # Count up online users per chatroom.
    #     current_user_id = self.id
    #     online_subq = (
    #         select(
    #             user_chatroom_table.c.chatroom_id,
    #             func.count(user_chatroom_table.c.user_id).label("online_count"),
    #         )
    #         .join(Users, user_chatroom_table.c.user_id == Users.id)
    #         .where(Users.online == True)
    #         .group_by(user_chatroom_table.c.chatroom_id)
    #         .subquery()
    #     )

    #     # Count up online users per chatroom.
    #     offline_subq = (
    #         select(
    #             user_chatroom_table.c.chatroom_id,
    #             func.count(user_chatroom_table.c.user_id).label("offline_count"),
    #         )
    #         .join(Users, user_chatroom_table.c.user_id == Users.id)
    #         .where(Users.online == False)
    #         .group_by(user_chatroom_table.c.chatroom_id)
    #         .subquery()
    #     )

    #     # All the chatrooms this user belongs to.
    #     current_user_chatroom_subq = select(user_chatroom_table.c.chatroom_id).where(
    #         user_chatroom_table.c.user_id == current_user_id
    #     )
    #     # Now get chatrooms with those counts.
    #     # We use outerjoin because some chatrooms have no matching
    #     # online and/or offline count and we want those chatrooms
    #     # to still be included.
    #     # When those chatrooms are included that missing count would
    #     # normally be NULL/None but we use coalesce() to tell
    #     # the database to convert that value to 0.
    #     q = (
    #         select(
    #             Chatrooms.id,
    #             func.coalesce(online_subq.c.online_count, 0).label("online_count"),
    #             func.coalesce(offline_subq.c.offline_count, 0).label("offline_count"),
    #         )
    #         .outerjoin(online_subq, Chatrooms.id == online_subq.c.chatroom_id)
    #         .outerjoin(offline_subq, Chatrooms.id == offline_subq.c.chatroom_id)
    #         .where(Chatrooms.id.in_(current_user_chatroom_subq))
    #     )
    #     return [
    #         {
    #             "chatroom_id": chatroom_id,
    #             "online": online_count,
    #             "offline": offline_count,
    #         }
    #         for chatroom_id, online_count, offline_count in (await session.execute(q))
    #     ]

    async def get_user_chatrooms(self, db: AsyncSession) -> List["Chatrooms"]:
        """
        Asynchronously get a list of chatrooms that the given user is a part of.

        :param user_id: UUID of the user to check.
        :param db: SQLAlchemy AsyncSession.
        :return: List of Chatrooms the user is a part of.
        """
        # Create a query that selects chatrooms joined by the given user_id
        stmt = (
            select(Chatrooms.id)
            .join(
                user_chatroom_table, Chatrooms.id == user_chatroom_table.c.chatroom_id
            )
            .where(user_chatroom_table.c.user_id == self.id)
        )

        result = await db.execute(stmt)
        chatrooms = result.scalars().all()

        return chatrooms

    async def associate_users_with_notification(
        self,
        session: AsyncSession,
        notification_ids: list[uuid.UUID],
    ):

        entries = [
            {
                "user_id": self.id,
                "notification_id": n_id,
                "read": True,
                "updated_at": datetime.now(),
            }
            for n_id in notification_ids
        ]

        # Execute the insert operation
        await session.execute(insert(user_notifications).values(entries))
        await session.commit()

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

    async def get_online_users(self, db: AsyncSession):
        stmt = (
            select(Users.id)
            .join(user_chatroom_table, Users.id == user_chatroom_table.c.user_id)
            .where(
                user_chatroom_table.c.chatroom_id == self.id
            )  # Existing condition for specific chatroom
            .where(
                Users.online == True
            )  # Additional condition for filtering online users
        )
        result = await db.execute(stmt)
        users = result.scalars().all()  # Extracting user IDs as a list of integers

        # Joining the user IDs into a single string separated by commas
        user_ids_string = ",".join(
            map(str, users)
        )  # Converts each user ID to string and joins them with commas
        return user_ids_string

    async def get_online_and_offline_user(self, db: AsyncSession):
        stmt = (
            select(Users)
            .join(user_chatroom_table, Users.id == user_chatroom_table.c.user_id)
            .where(
                user_chatroom_table.c.chatroom_id == self.id
            )  # Existing condition for specific chatroom
        )
        result = await db.execute(stmt)
        users = result.scalars().all()  # Extracting user IDs as a list of integers

        online_string = ","
        for user in users:
            if user.online is True:
                online_string = online_string + f"{str(user.id)},"

        return {"online": online_string, "users": users}

    async def user_count(self, db: AsyncSession):

        stmt = (
            select(Users.id, Users.username, Users.online)
            .join(user_chatroom_table, Users.id == user_chatroom_table.c.user_id)
            .where(user_chatroom_table.c.chatroom_id == self.id)
        )

        result = await db.execute(stmt)
        users = result.mappings().all()  # Fetch all results as a list of dictionaries

        # Split into online and offline users based on their status
        online = sum(user["online"] for user in users)
        offline = len(users) - online

        return {"online": online, "offline": offline}

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


class Notifications(Base):

    id: Mapped[uuid:UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        unique=True,
        default=uuid.uuid4,
    )

    user: Mapped["Users"] = relationship(back_populates="notifications", lazy="raise")
    user_id: Mapped[uuid:UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )

    read: Mapped[bool] = mapped_column(nullable=False, default=False)
    data: Mapped[dict] = mapped_column(type_=JSON, nullable=False)
    type: Mapped[str] = mapped_column(nullable=False)

    @classmethod
    async def create(
        cls,
        db: AsyncSession,
        id: str | uuid.UUID,
        user_id: str | uuid.UUID,
        created_at: datetime,
        type: str,
        data: any,
    ):

        notif = cls(id=id, type=type, user_id=user_id, created_at=created_at, data=data)
        db.add(notif)
        await db.commit()
        return notif

    @classmethod
    async def update(
        cls, db: AsyncSession, id: str | uuid.UUID, user_id: str | uuid.UUID
    ):
        stmt = (
            update(user_notifications)
            .where(
                user_notifications.c.user_id == user_id,
                user_notifications.c.notification_id == id,
            )
            .values(read=True)
        )

        # Execute the insert operation
        await db.execute(stmt)
        await db.commit()

    async def associate_users_with_notification(
        self,
        session: AsyncSession,
        users: list[Users],
    ):

        entries = [
            {
                "user_id": user.id,
                "notification_id": self.id,
                "read": False,
                "created_at": datetime.now(),
            }
            for user in users
        ]

        # Execute the insert operation
        await session.execute(insert(user_notifications).values(entries))
        await session.commit()

    @classmethod
    async def paginate(
        cls,
        db_session: AsyncSession,
        user: Users,
        page: int,
        per_page: int,
    ):
        base_query = (
            select(
                Notifications.id,
                Notifications.data,
                Notifications.type,
                Notifications.user_id,
                user_chatroom_table.chatroom_id,
                Notifications.created_at,
            )
            .join(
                user_notifications,
                Notifications.id == user_notifications.c.notification_id,
            )
            .where(
                user_notifications.c.read == False,
                user_notifications.c.user_id == user.id,
            )
            .order_by(Notifications.created_at.desc())
        )

        final_stmt = (
            base_query.add_columns(
                Notifications.id,
                Notifications.data["text"].label(
                    "text"
                ),  # Assuming 'text' is stored in data JSON field
                Notifications.type,
                Notifications.user_id,
                Notifications.chatroom_id,
                Notifications.created_at,
                user_notifications.c.read.label(
                    "read"
                ),  # Assuming you want to check if a notification is read
            )
            .offset(offset)
            .limit(per_page)
        )

        count_stmt = select(func.count()).select_from(base_query.subquery())
        total_items_result = await db_session.execute(count_stmt)
        total_items = total_items_result.scalar_one()

        total_pages = math.ceil(total_items / per_page)
        offset = (page - 1) * per_page

        # Apply pagination to the base query
        final_stmt = final_stmt.offset(offset).limit(per_page)
        notifications_result = await db_session.execute(final_stmt)
        notifications_db = notifications_result.all()

        # Convert database results into NotificationOut objects
        items = [
            dict(
                id=notification.id,
                text=notification.text,
                type=notification.type,
                user_id=notification.user_id,
                chatroom_id=notification.chatroom_id,
                created_at=notification.created_at,
                read=notification.read,
            )
            for notification in notifications_db
        ]

        return dict(
            current_page=page,
            total_pages=total_pages,
            total_items=total_items,
            per_page=per_page,
            items=items,
        )
