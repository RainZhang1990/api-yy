import logging

import grpc

from core.config import Config
from core.singleton import Singleton
from core.server_status import get_server_status
from google.protobuf.struct_pb2 import Struct
from microserver.pb import pbmsgbox_pb2
from microserver.mserver import MServer


class MsgBoxServer(metaclass=Singleton):
    async def create_group_message(self, group_message_id, product_id, msg_title, msg_content, from_id,
                                   request_id=None):
        content = Struct()
        try:
            content.update(msg_content)
            message_body = pbmsgbox_pb2.MessageBody(msg_title=msg_title, msg_content=content)
            msg = pbmsgbox_pb2.GroupMessageCreateRequest(group_message_id=group_message_id, product_id=product_id,
                                                         message_body=message_body, from_id=from_id)
            await MServer().call("msgbox-server", "CreateGroupMessage", msg, request_id)
        except grpc.RpcError as e:
            msg = "create group message except. code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return e.details()

    # async def add_message(self, message_id, product_id, msg_type, message, request_id=None):
    #     messages = pbmsgbox_pb2.MessageAddRequest(message_id=message_id, product_id=product_id, msg_type=msg_type,
    #                                               message=message)
    #     msg = pbmsgbox_pb2.MessageAddRequests(messages=messages)
    #     await MServer().call("msgbox-server", "Add", msg, request_id)

    async def query_message(self, product_id, to_id, msg_type, per_page, from_message_id=(1 << 63) - 1, space_id=None,
                            request_id=None):
        try:
            msg = pbmsgbox_pb2.MessageQueryRequest(product_id=product_id, to_id=to_id, from_message_id=from_message_id,
                                                   per_page=per_page, msg_type=msg_type, space_id=space_id)
            query_response = await MServer().call("msgbox-server", "Query", msg, request_id)

            return query_response

        except grpc.RpcError as e:
            msg = "query message except. code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

    async def delete_message(self, message_id, to_id, request_id=None):
        try:
            msg = pbmsgbox_pb2.MessageItemRequest(message_id=message_id, to_id=to_id)
            await MServer().call("msgbox-server", "Delete", msg, request_id)

        except grpc.RpcError as e:
            msg = "delete message except. code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)
            return e.code()

    async def delete_all_message(self, product_id, to_id, space_id, msg_type, request_id=None):
        try:
            msg = pbmsgbox_pb2.MessageQueryAllRequest(product_id=product_id, to_id=to_id, space_id=space_id,
                                                      msg_type=msg_type)
            await MServer().call("msgbox-server", "DeleteAll", msg, request_id)

        except grpc.RpcError as e:
            msg = "delete all message except. code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)
            return e.code()

    async def set_message_as_read(self, message_id, to_id, request_id=None):
        try:
            msg = pbmsgbox_pb2.MessageItemRequest(message_id=message_id, to_id=to_id)
            await MServer().call("msgbox-server", "Read", msg, request_id)

        except grpc.RpcError as e:
            msg = "set message is read except. code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)
            return e.code()

    async def set_all_message_as_read(self, product_id, to_id, space_id, msg_type, request_id=None):
        try:
            msg = pbmsgbox_pb2.MessageQueryAllRequest(product_id=product_id, to_id=to_id, space_id=space_id,
                                                      msg_type=msg_type)
            await MServer().call("msgbox-server", "ReadAll", msg, request_id)
        except grpc.RpcError as e:
            msg = "set all message is read except. code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)
            return e.code()

    async def set_message_as_unread(self, message_id, to_id, request_id=None):
        try:
            msg = pbmsgbox_pb2.MessageItemRequest(message_id=message_id, to_id=to_id)
            await MServer().call("msgbox-server", "UnRead", msg, request_id)
        except grpc.RpcError as e:
            msg = "set message is unread except. code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)
            return e.code()

    async def get_unread_count(self, product_id, msg_type, to_id, space_id=None, request_id=None):
        try:
            msg = pbmsgbox_pb2.MessageUnReadCountRequest(product_id=product_id, to_id=to_id, msg_type=msg_type,
                                                         space_id=space_id)
            pbcount = await MServer().call("msgbox-server", "GetUnReadCount", msg, request_id)
            return pbcount.count
        except grpc.RpcError as e:
            msg = "set message is unread except. code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)
            return e.code()
