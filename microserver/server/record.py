import logging
import datetime
import time
import grpc
from core.singleton import Singleton
from microserver.pb import pbrecord_pb2
from microserver.mserver import MServer
from google.protobuf.timestamp_pb2 import Timestamp


class RecordServer(metaclass=Singleton):
    async def get_growth_list(self, account_id, space_id, creator_id, request_id):
        """
        
        :param acccount_id: 
        :param request_id: 
        :return: growth_list
        """
        try:
            msg = pbrecord_pb2.GetGrowthListRequest(account_id=account_id, space_id=space_id, creator_id=creator_id)
            pb_growth_list = await MServer().call("record-server", "GetGrowthList", msg, request_id)

            return pb_growth_list

        except grpc.RpcError as e:
            # except grpc._channel._Rendezvous as e:
            msg = "get growth list. code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def add_record(self, account_id, height, weight, head_circumference, record_at, space_id, creator_id, request_id):
        """
        
        :param account_id: 
        :param height: 
        :param weight: 
        :param head_circumference: 
        :param record_at: 
        :return: 
        """
        try:
            date = Timestamp()
            date.FromDatetime(datetime.datetime.strptime(record_at.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S"))
            msg = pbrecord_pb2.RecordDetail(account_id=account_id, height=height, weight=weight,
                                            head_circumference=head_circumference, record_at=date, space_id=space_id,
                                            creator_id=creator_id)

            result = await MServer().call("record-server", "AddRecord", msg, request_id)
            return result.is_done, result.message

        except grpc.RpcError as e:
            # except grpc._channel._Rendezvous as e:
            msg = "add record. code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def delete_record(self, growth_id, space_id, creator_id, request_id):
        """
        
        :param growth_id: 
        :param request_id: 
        :return: 
        """
        try:
            msg = pbrecord_pb2.DeleteGrowthDetailRequest(growth_id=growth_id, space_id=space_id, creator_id=creator_id)
            result = await MServer().call("record-server", "DeleteGrowthDetail", msg, request_id)

            return result.is_done, result.message

        except grpc.RpcError as e:
            # except grpc._channel._Rendezvous as e:
            msg = "delete record. code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def update_record(self, growth_id, height, weight, head_circumference, record_at, space_id, creator_id, request_id):
        """
        
        :param params: 
        :param request_id: 
        :return: 
        """
        try:
            date = Timestamp()
            date.FromDatetime(datetime.datetime.strptime(record_at.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S"))
            msg = pbrecord_pb2.GrowthDetail(growth_id=growth_id, height=height, weight=weight,
                                            head_circumference=head_circumference, record_at=date, space_id=space_id,
                                            creator_id=creator_id)
            result = await MServer().call("record-server", "UpdateGrowthDetail", msg, request_id)

            return result.is_done, result.message

        except grpc.RpcError as e:
            # except grpc._channel._Rendezvous as e:
            msg = "update record. code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def get_birth_record(self, space_id, creator_id, account_id, record_at, request_id):
        """

        :param space_id:
        :param creator_id:
        :param account_id:
        :param request_id:
        :return:
        """
        try:
            date = Timestamp()
            date.FromDatetime(datetime.datetime.strptime(record_at.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S"))
            msg = pbrecord_pb2.GetBirthRecordRequest(space_id=space_id, creator_id=creator_id, account_id=account_id, record_at=date)
            result = await MServer().call("record-server", "GetBirthRecord", msg, request_id)

            return result

        except grpc.RpcError as e:
            # except grpc._channel._Rendezvous as e:
            msg = "update record. code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None