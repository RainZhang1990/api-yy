import logging

import grpc

from core.config import Config
from core.singleton import Singleton
from core.server_status import get_server_status
from microserver.pb import pbzid_pb2
from microserver.mserver import MServer


class ZIDServer(metaclass=Singleton):
    async def generate(self, request_id=None):
        """生成一个全局唯一ID
        Returns:
            int -- ID
        """

        ids = await self._call(1, request_id)
        return ids[0] if ids else None

    async def generate_multi(self, number, request_id=None):
        """生成多个全局唯一ID

        Arguments:
            number int -- 生成数量

        Returns:
            list -- 返回由ID组成的list
        """

        return await self._call(number, request_id)

    async def _call(self, number, request_id):
        try:
            request = pbzid_pb2.IDRequest()
            request.number = number

            pb_ids = await MServer().call("zid-server", "Query", request, request_id)
            return pb_ids.IDs

        except grpc.RpcError as e:
            # except grpc._channel._Rendezvous as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None
