import json
import random
import libs.validator
from tornado.web import HTTPError
from handler.api import APIHandler
import time
from tornado.web import HTTPError, RequestHandler
from tornado.escape import json_decode, json_encode

class TestHandler(RequestHandler):
    async def get(self):
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        result = dict(status=0, message='Hello World!')
        self.finish(json_encode(result))
        

class NotFoundHandler(RequestHandler):
    def prepare(self):
        raise HTTPError(404)
