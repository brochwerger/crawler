import redis
from abc import ABC, abstractmethod

class BasicKVS(ABC):
    kvs = {}

    def put(self, key, value, aging=None):
        BasicKVS.kvs[key] = value

    def get(self, key):

        if key in BasicKVS.kvs.keys():
            return BasicKVS.kvs[key]
        else:
            return None

class RedisKVS(BasicKVS):

    kvs = None

    def __init__(self, host):

        if RedisKVS.kvs == None:
            RedisKVS.kvs = redis.Redis(host=host, port=6379, db=0)
            RedisKVS.kvs.flushdb()

    def put(self, key, value, aging=None):
        # aging parameter in minutes, redis expect the expiration period in seconds
        RedisKVS.kvs.set(key, value, ex=(aging * 60) if aging else None)

    def get(self, key):
        return RedisKVS.kvs.get(key)


