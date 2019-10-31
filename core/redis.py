# import redis

from core.config import Config, Secret

REDIS_POOL = None


def init():
    global REDIS_POOL
    REDIS_POOL = redis.ConnectionPool(host=Secret().redis.get('host'), port=Secret().redis.get('port'),
                                      password=Secret().redis.get('password'),
                                      db=Config().redis.get('db'),
                                      max_connections=Config().redis.get('max_connections'))


def redis_set(key, value, timeout):
    key = Config().redis.get("prefix") + ":" + key
    rd = redis.Redis(connection_pool=REDIS_POOL)
    rd.setex(key, value, timeout)


def redis_get(key):
    key = Config().redis.get("prefix") + ":" + key
    rd = redis.Redis(connection_pool=REDIS_POOL)
    data = rd.get(key)
    return data

def redis_del(key):
    key = Config().redis.get("prefix") + ":" + key
    rd = redis.Redis(connection_pool=REDIS_POOL)
    rd.delete(key)

def redis_del_list(key):
    key = Config().redis.get("prefix") + ":" + key
    rd = redis.Redis(connection_pool=REDIS_POOL)
    key_list = rd.keys(pattern=key)
    if key_list:
        rd.delete(*[k.decode() for k in key_list])
