import redis
import logging
from core.config import Config
from controller.feature import *
import _thread
import time

REDIS_POOL = None
chan_sub = None

def init():
    global REDIS_POOL
    global chan_sub
    REDIS_POOL = redis.ConnectionPool(host=Config().redis.get('host'), port=Config().redis.get('port'),
                                      password=Config().redis.get('password'),
                                      db=Config().redis.get('db'),
                                      decode_responses=True, # byte -> string
                                      max_connections=Config().redis.get('max_connections'))
    chan_sub = Config().redis.get('chan_sub')
    _thread.start_new_thread(msg_process)

def msg_process():
    retry_interval = Config().redis.get('retry_interval')
    while True:
        # try:
        for msg in subscribe().listen():
            if  msg['type']=='message': 
                m=msg['data'].split('_')
                FeatureManager().update_feature(m[0],m[1])
        # except Exception as e:
        #     logging.critical(e)
        #     time.sleep(retry_interval)
        

def publish(msg):
    rd = redis.Redis(connection_pool=REDIS_POOL)
    rd.publish(chan_sub, msg)

def subscribe():
    rd = redis.Redis(connection_pool=REDIS_POOL)
    pub=rd.pubsub()
    pub.subscribe(chan_sub)
    return pub

def redis_set(prefix, key, value, timeout=None):
    key = prefix + '_' + key
    rd = redis.Redis(connection_pool=REDIS_POOL)
    rd.setex(key, value, timeout)


def redis_get(prefix, key):
    key = prefix + '_' + key
    rd = redis.Redis(decode_responses=True, connection_pool=REDIS_POOL)
    data = rd.get(key)
    return data


def redis_del(prefix, key):
    key = prefix + '_' + key
    rd = redis.Redis(connection_pool=REDIS_POOL)
    rd.delete(key)


def redis_del_list(prefix, key):
    key = prefix + '_' + key
    rd = redis.Redis(connection_pool=REDIS_POOL)
    key_list = rd.keys(pattern=key)
    if key_list:
        rd.delete(*[k.decode() for k in key_list])


def redis_hset(prefix, name, key, value):
    name = prefix + '_' + name
    rd = redis.Redis(connection_pool=REDIS_POOL)
    rd.hset(name, key, value)


def redis_hgetall(prefix, name):
    name = prefix + '_' + name
    rd = redis.Redis(decode_responses=True, connection_pool=REDIS_POOL)
    data = rd.hgetall(name)
    return data


def redis_hdel(prefix, name, *keys):
    name = prefix + '_' + name
    rd = redis.Redis(connection_pool=REDIS_POOL)
    rd.hdel(name, *keys)


def redis_lpush(prefix, name, values):
    name = prefix + '_' + name
    rd = redis.Redis(connection_pool=REDIS_POOL)
    rd.lpush(name, values)


def redis_rpop(prefix, name):
    name = prefix + '_' + name
    rd = redis.Redis(decode_responses=True, connection_pool=REDIS_POOL)
    data = rd.rpop(name)
    return data


def redis_lrange(prefix, name, start=0, end=-1):
    name = prefix + '_' + name
    rd = redis.Redis(decode_responses=True, connection_pool=REDIS_POOL)
    data = rd.lrange(name, start, end)
    return data
