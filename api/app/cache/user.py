import uuid
from redis.asyncio.cluster import (
    ClusterNode as AsyncClusterNode,
    RedisCluster as AsyncRedisCluster,
)

from typing import List
from app.cache.key_schema import KeySchema
from app.schema.notifications import NotificationType, Notification, Message


class CacheUser:
    def __init__(
        self,
        id: str | uuid.UUID,
        username: str,
    ):
        self.id = id
        self.username = username
        self.keys = KeySchema()

    def store_message(self, pipeline, message: Message):
        n = Notification(event=message, id=str(uuid.uuid4()))
        mapping = n.hash_dict()
        key = self.keys.notifications(notification_id=n.id)
        pipeline.hset(key, mapping)
        user_key = self.keys.user_notifications(user_id=self.id)
        pipeline.lpush(user_key, str(n.id))

    async def get_notification(
        self, redis, notification_id: str | uuid.UUID, pipe: bool = False
    ):
        key = self.keys.notifications(notification_id=notification_id)
        if pipe is True:
            redis.hgetall(key)
        elif pipe is False:
            data = await redis.hgetall(key)

    async def get_notifications(self, redis) -> List[Notification]:
        user_key = self.keys.user_notifications(user_id=self.id)
        notification_ids = await redis.lrange(user_key, 0, -1)
        pipe = await redis.pipeline()

    @classmethod
    async def add_notitifcations(
        redis, users: List["CacheUser"], notification: Message
    ):
        pipe = await redis.pipeline()
        for user in users:
            if notification == Message:
                store = user.store_message(pipeline=pipe, message=notification)

        await pipe.execute()
