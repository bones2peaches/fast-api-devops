from redis.asyncio.cluster import (
    ClusterNode as AsyncClusterNode,
    RedisCluster as AsyncRedisCluster,
)


redis_cluster = AsyncRedisCluster.from_url(
    "redis://:@redis-node-1:7000",
    decode_responses=True,
    require_full_coverage=False,
)


async def get_redis():

    session = await redis_cluster.initialize()
    # logger.debug(f"ASYNC Pool: {engine.pool.status()}")
    yield session
