import logging
import datetime

import grpc

from core.singleton import Singleton
from microserver.pb import pbpush_pb2
from microserver.mserver import MServer
from google.protobuf.timestamp_pb2 import Timestamp


class PushServer(metaclass=Singleton):
    async def update_device(self, device_id, account_id, product_id, app_id, app_version, push_token, push_active,
                            request_id=None, **info):

        try:
            info = info.get('info')
            device_info = pbpush_pb2.DeviceInfo(brand=info.get("brand"), model=info.get("model"),
                                                name=info.get("device_name"), pixel_ratio=info.get("pixel_ratio"),
                                                screen_width=info.get("screen_width"),
                                                screen_height=info.get("screen_height"))
            system_info = pbpush_pb2.SystemInfo(name=info.get("system_name"), version=info.get("system_version"),
                                                language=info.get("system_language"))

            msg = pbpush_pb2.Device(device_id=device_id, account_id=account_id, product_id=product_id, app_id=app_id,
                                    app_version=app_version, push_token=push_token, push_active=push_active,
                                    device_info=device_info, system_info=system_info)

            await MServer().call("push-server", "UpdateDevice", msg, request_id)

            return

        except grpc.RpcError as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)
            return e.details()

    async def send(self, product_id, app_id, space_id, payload, msg_type, from_id, job_filter, level, message,
                   expiration_at_hours=48, additional_params=None, schedule_at=None, request_id=None):
        """

        :param product_id:
        :param app_id:
        :param space_id:
        :param payload:
        :param msg_type: im(保留）, im_group （保留）, feed ,system
        :param from_id:
        :param job_filter:
        :param level:
        :param message:
        :param expiration_at:
        :param schedule_at:
        :param request_id:
        :return:
        """
        msg_object = pbpush_pb2.MessageObject(msg_type=msg_type, message_body=message, from_id=from_id,
                                              space_id=space_id)
        expiration_at_stamp = Timestamp()
        expiration_at_stamp.FromDatetime(datetime.datetime.now() + datetime.timedelta(hours=expiration_at_hours))
        msg = pbpush_pb2.PushJob(product_id=product_id, app_id=app_id, job_filter=job_filter, level=level,
                                 payload=payload,schedule_at=schedule_at, expiration_at=expiration_at_stamp,
                                 msg_object=msg_object, additional_params=additional_params)

        push_job = await MServer().call("push-server", "Send", msg, request_id)

        if push_job:
            return push_job.job_id

    async def get_job_status(self, job_id, request_id=None):
        try:
            msg = pbpush_pb2.PushJobID(job_id=job_id)
            job_status = await MServer().call("push-server", "GetJobStatus", msg, request_id)
            return job_status

        except grpc.RpcError as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)
            return e.details()