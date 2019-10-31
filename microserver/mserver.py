import logging
import sys
import uuid

import grpc

from tornado.ioloop import IOLoop
from tornado.gen import Future
from tornado.web import HTTPError

from core.config import Config
from core.singleton import Singleton

from .pb import pbaccount_pb2_grpc
from .pb import pbwxcc_pb2_grpc
from .pb import pbsms_pb2_grpc
from .pb import pbzid_pb2_grpc
from .pb import pbmembership_pb2_grpc
from .pb import pbspace_pb2_grpc
from .pb import pbvaccine_pb2_grpc
from .pb import pbrecord_pb2_grpc
from .pb import pbfeed_pb2_grpc
from .pb import pbmsgbox_pb2_grpc
from .pb import pbpush_pb2_grpc

def _fwrap(f, gf):
    try:
        f.set_result(gf.result())
    except Exception as e:
        f.set_exception(e)


def fwrap(gf, ioloop=None):
    '''
        Wraps a GRPC result in a future that can be yielded by tornado

        Usage::

            @coroutine
            def my_fn(param):
                result = yield fwrap(stub.function_name.future(param, timeout))

    '''
    f = Future()

    if ioloop is None:
        ioloop = IOLoop.current()

    gf.add_done_callback(lambda _: ioloop.add_callback(_fwrap, f, gf))
    return f


class MServer(metaclass=Singleton):
    def __init__(self):

        self.channels = dict()

    def _ensure_server(self, server):
        """
        ensure connection of server is alive
        """
        if server not in self.channels or not self.channels[server]:
            server_cfg = Config().microserver.get(server)
            channel = grpc.insecure_channel(server_cfg.get("server"))
            self.channels[server] = channel

    def get_stub(self, server):
        """
        get stub of server
        """

        server_cfg = Config().microserver.get(server)
        if not server_cfg:
            return None

        self._ensure_server(server)

        stub = getattr(str_to_class(server_cfg.get("pb2_grpc")),
                       server_cfg.get("stub"))
        return stub(self.channels[server])

    async def call(self, server, method, msg, request_id, timeout=60):

        # get stub
        stub = self.get_stub(server)
        if not stub:
            raise Exception(server+' server not found')

        try:
            method_func = getattr(stub, method)
            response = await fwrap(method_func.future(msg, timeout=timeout, metadata=self._gen_metadata(request_id)))

            return response
        except grpc.RpcError as e:
            log_message = "call grpc server {}.{} except. code: {}, details: {}".format(server, method, e.code(), e.details())
            logging.warning(log_message)
            raise e

    def _gen_metadata(self, request_id):
        request_id = self._ensure_request_id(request_id)
        return [(b'x-request-id', request_id.encode('utf-8'))]

    def _ensure_request_id(self, request_id):
        if not request_id:
            return str(uuid.uuid4())
        return request_id


def str_to_class(str):
    return getattr(sys.modules[__name__], str)
