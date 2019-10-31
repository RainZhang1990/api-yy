import logging

import grpc

from core.config import Config
from core.singleton import Singleton
from core.server_status import get_server_status
from microserver.pb import pbmembership_pb2
from microserver.mserver import MServer

class MembershipServer(metaclass=Singleton):
    async def set_storage_change(self, account_id, changed_value, title, details, request_id):
        """
        
        :param account_id: 
        :param changed_value: 
        :param title: 
        :param details: 
        :return: 
        """
        try:
            msg = pbmembership_pb2.StorageChange(account_id=account_id, changed_value=changed_value, title=title,
                                                 details=details)

            result = await MServer().call(
                "membership-server", "SetStorageChange", msg, request_id)
            return result.is_done

        except grpc.RpcError as e:
            # except grpc._channel._Rendezvous as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def set_total_storage_change(self, account_id, changed_value, title, details, request_id):
        """
        
        :param account_id: 
        :param changed_value: 
        :param title: 
        :param details: 
        :return: 
        """
        try:
            msg = pbmembership_pb2.StorageChange(account_id=account_id, changed_value=changed_value, title=title,
                                                 details=details)

            result = await MServer().call(
                "membership-server", "SetTotalStorageChange", msg, request_id)
            return result.is_done

        except grpc.RpcError as e:
            # except grpc._channel._Rendezvous as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None
