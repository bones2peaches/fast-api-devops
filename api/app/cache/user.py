import uuid
from redis.asyncio.cluster import (
    ClusterNode as AsyncClusterNode,
    RedisCluster as AsyncRedisCluster,
)


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

        n_id = str(uuid.uuid4())
        notif = Notification(event=message, id=n_id)
        mapping = notif.hash_dict()
        key = self.keys.notifications(notification_id=n_id)
        pipeline.hset(key, mapping)
