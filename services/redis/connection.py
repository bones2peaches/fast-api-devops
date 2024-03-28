import redis
from redis.exceptions import RedisError


redis_nodes = [
    {'host': 'localhost', 'port': 7000},
    {'host': 'localhost', 'port': 7001},
    {'host': 'localhost', 'port': 7002},
    {'host': 'localhost', 'port': 7003},
    {'host': 'localhost', 'port': 7004},
    {'host': 'localhost', 'port': 7005},
]# Replace with the IP addresses and ports of your Redis nodes

def ping_redis_cluster(nodes):
    for i, node in enumerate(nodes):
        try:
            r = redis.StrictRedis(host=node['host'], port=node['port'])
            response = r.ping()
            if response:
                print(f'Node {i+1} ({node["host"]}:{node["port"]}) is up and running.')
            else:
                print(f'Node {i+1} ({node["host"]}:{node["port"]}) did not respond to PING.')
        except RedisError as e:
            print(f'Error connecting to Node {i+1} ({node["host"]}:{node["port"]}): {e}')

if __name__ == '__main__':
    ping_redis_cluster(redis_nodes)
