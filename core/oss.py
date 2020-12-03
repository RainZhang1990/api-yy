import logging
import oss2
from functools import wraps

from core.config import Config

oss_bucket = None

def init():
    global oss_bucket
    oss_bucket = create(
        Config().oss["access_id"],
        Config().oss["access_secret"],
        Config().oss["bucket"],
        Config().oss["endpoint"],
    )

def create(access_id, access_secret, bucket, endpoint):
    auth = oss2.Auth(access_id, access_secret)
    oss_bucket = oss2.Bucket(auth, endpoint, bucket)
    return oss_bucket

# def blocking(method):
#     """Wraps the method in an async method, and executes the function on `self.executor`."""

#     @wraps(method)
#     @tornado.gen.coroutine
#     def wrapper(self, *args, **kwargs):
#         fut = self.executor.submit(method, self, *args, **kwargs)
#         return (yield fut)

#     return wrapper


