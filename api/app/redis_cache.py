from redis.asyncio.cluster import (
    ClusterNode as AsyncClusterNode,
    RedisCluster as AsyncRedisCluster,
)


nodes = [
    AsyncClusterNode(r"redis-node-1", 7000),
    AsyncClusterNode(r"redis-node-2", 7001),
    AsyncClusterNode(r"redis-node-3", 7002),
    AsyncClusterNode(r"redis-node-4", 7003),
    AsyncClusterNode(r"redis-node-5", 7004),
    AsyncClusterNode(r"redis-node-6", 7005),
]


async def get_redis():

    async with AsyncRedisCluster(startup_nodes=nodes) as rc:

        yield rc
