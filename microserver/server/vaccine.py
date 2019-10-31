import logging

import grpc
from tornado.web import HTTPError
from core.singleton import Singleton
from microserver.pb import pbvaccine_pb2
from microserver.mserver import MServer


class VaccineServer(metaclass=Singleton):
    async def get_vaccine_detail_list(self, request_id):
        try:
            msg = pbvaccine_pb2.EmptyData()
            pb_detail_list = await MServer().call("vaccine-server", "SearchVaccineAll", msg, request_id)
            return pb_detail_list

        except grpc.RpcError as e:
            # except grpc._channel._Rendezvous as e:
            msg = "get vaccine detail list. code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def search_vaccine(self, vaccine_id, request_id):
        try:
            msg = pbvaccine_pb2.VaccineId(vaccine_id=vaccine_id)
            pb_detail = await MServer().call("vaccine-server", "SearchVaccine", msg, request_id)
            return pb_detail

        except grpc.RpcError as e:
            # except grpc._channel._Rendezvous as e:
            msg = "get vaccine detail . code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

    async def get_injection_details(self, account_id, space_id, creator_id, request_id):
        try:
            msg = pbvaccine_pb2.GetInjectionLogRequest(account_id=account_id, space_id=space_id, creator_id=creator_id)
            pb_injection_log = await MServer().call("vaccine-server", "GetInjectionLog", msg, request_id)
            return pb_injection_log

        except grpc.RpcError as e:
            msg = "get injection details. code: {}, details:{}".format(e.code(), e.details())
            if e.code().__dict__.get('_name_') == 'PERMISSION_DENIED':
                raise HTTPError(-1, "permission denied", reason="权限不足！")
            logging.warning(msg)

            return None

    async def update_no_indected(self, account_id, vaccine_id, injection_no, space_id, creator_id, request_id):
        try:
            msg = pbvaccine_pb2.InjectionParam(account_id=account_id, vaccine_id=vaccine_id, injection_no=injection_no,
                                               space_id=space_id, creator_id=creator_id)
            result = await MServer().call("vaccine-server", "UpdateNoInjected", msg, request_id)

            return result.is_done

        except grpc.RpcError as e:
            msg = "update no indected. code: {}, details:{}".format(e.code(), e.details())
            if e.code().__dict__.get('_name_') == 'PERMISSION_DENIED':
                raise HTTPError(-1, "permission denied", reason="权限不足！")
            logging.warning(msg)

            return None

    async def update_plan_inject(self, account_id, vaccine_id, injection_no, space_id, creator_id, date_of_inoculation,
                           request_id):
        try:
            msg = pbvaccine_pb2.InjectionParam(account_id=account_id, vaccine_id=vaccine_id, injection_no=injection_no,
                                               date_of_inoculation=date_of_inoculation, space_id=space_id,
                                               creator_id=creator_id)
            result = await MServer().call("vaccine-server", "UpdatePlanInject", msg, request_id)

            return result.is_done

        except grpc.RpcError as e:
            msg = "update plan inject. code: {}, details:{}".format(e.code(), e.details())
            if e.code().__dict__.get('_name_') == 'PERMISSION_DENIED':
                raise HTTPError(-1, "permission denied", reason="权限不足！")
            logging.warning(msg)

            return None

    async def update_injected(self, account_id, vaccine_id, injection_no, space_id, creator_id, date_of_inoculation,
                        request_id):
        try:
            msg = pbvaccine_pb2.InjectionParam(account_id=account_id, vaccine_id=vaccine_id, injection_no=injection_no,
                                               date_of_inoculation=date_of_inoculation, space_id=space_id,
                                               creator_id=creator_id)
            result = await MServer().call("vaccine-server", "UpdateInjected", msg, request_id)

            return result.is_done

        except grpc.RpcError as e:
            msg = "update inject. code: {}, details:{}".format(e.code(), e.details())
            if e.code().__dict__.get('_name_') == 'PERMISSION_DENIED':
                raise HTTPError(-1, "permission denied", reason="权限不足！")
            logging.warning(msg)

            return None
