import json
import time
import datetime
import libs.validator
from tornado.web import HTTPError
from handler.api import APIHandler
from microserver.server.vaccine import VaccineServer
from microserver.server.space import SpaceServer
from core.config import Config
from core import redis as rd
from model.vaccine import Vaccine, InjectDetail
from .api import authenticated_async
from libs import zbase62


class GetInjectionDetail(APIHandler):
    @authenticated_async
    async def post(self):
        # todo: 接种时间逻辑性校验
        try:
            libs.validator.space_id(self.post_data.get('space_id'))
        except libs.validator.ValidationError as e:
            self.send_to_client(-1, message=e.__str__())
            return
        injection_detail_key = 'injection_detail:{}'.format(zbase62.decode(self.post_data.get('space_id')))
        injection_detail = rd.redis_get(injection_detail_key)
        injection_detail = json.loads(str(injection_detail, encoding="utf-8")) if isinstance(injection_detail,
                                                                                             bytes) else injection_detail
        if not injection_detail:
            pb_space_detail = await SpaceServer().get_space_details(
                space_id=zbase62.decode(self.post_data.get('space_id')),
                request_id=self.request_id)
            if pb_space_detail:
                pb_detail_list = await VaccineServer().get_vaccine_detail_list(request_id=self.request_id)
                pb_injection_log = await VaccineServer().get_injection_details(account_id=pb_space_detail.owner_id,
                                                                               request_id=self.request_id,
                                                                               space_id=zbase62.decode(
                                                                                   self.post_data.get('space_id')),
                                                                               creator_id=self.current_user.account_id)

                inject_dict = {}
                if pb_injection_log:
                    for inject in pb_injection_log.inject_detail:
                        i = InjectDetail(inject).inject_detail
                        i["date_of_inoculation"] = time.strftime("%Y-%m-%d",
                                                                 time.localtime(inject.date_of_inoculation.seconds))
                        inject_dict[(i.get("vaccine_id"), i.get("injection_no"))] = i

                if pb_detail_list:
                    injection_detail = []
                    for vaccine in pb_detail_list.vaccines:
                        v = Vaccine(vaccine).vaccine
                        vd = inject_dict.get((v.get("vaccine_id"), v.get("injection_no")))
                        v['is_injected'] = vd.get("is_injected") if vd else None
                        v['date_of_inoculation'] = vd.get("date_of_inoculation") if vd else None
                        injection_detail.append(v)
                rd.redis_set(injection_detail_key, json.dumps(injection_detail), Config().redis.get("expire_list"))
        if injection_detail is not None:
            self.send_to_client(0, message='成功获取接种详情', response=injection_detail)
            return

        raise HTTPError(500, "get space failed", reason="服务器出错，请联系客服解决")


class SearchVaccine(APIHandler):
    """疫苗详情

    """

    @authenticated_async
    async def post(self):
        try:
            libs.validator.vaccine_id(self.post_data.get('vaccine_id'))
        except libs.validator.ValidationError as e:
            self.send_to_client(-1, message=e.__str__())
            return
        vaccine_detail_key = 'vaccine_detail:{}'.format(self.post_data.get('vaccine_id'))
        vaccine_detail = rd.redis_get(vaccine_detail_key)
        vaccine_detail = json.loads(str(vaccine_detail, encoding="utf-8")) if isinstance(vaccine_detail,
                                                                                         bytes) else vaccine_detail
        if not vaccine_detail:
            pb_detail = await VaccineServer().search_vaccine(vaccine_id=self.post_data.get("vaccine_id"),
                                                             request_id=self.request_id)
            vaccine_detail = InjectDetail(pb_detail).inject_detail
            rd.redis_set(vaccine_detail_key, json.dumps(vaccine_detail), Config().redis.get("expire_list"))
        if vaccine_detail is not None:
            self.send_to_client(0, message='查找成功', response=vaccine_detail)
            return

        raise HTTPError(500, "search vaccine failed", reason="服务器出错，请联系客服解决")


class UpdateNoIndected(APIHandler):
    """设置未接种

    """

    @authenticated_async
    async def post(self):
        try:
            libs.validator.space_id(self.post_data.get('space_id'))
            libs.validator.vaccine_id(self.post_data.get('vaccine_id'))
            libs.validator.record_at(self.post_data.get('date_of_inoculation'))
            libs.validator.injection_no(self.post_data.get('injection_no'))
        except libs.validator.ValidationError as e:
            self.send_to_client(-1, message=e.__str__())
            return
        pb_space_detail = await SpaceServer().get_space_details(space_id=zbase62.decode(self.post_data.get('space_id')),
                                                                request_id=self.request_id)
        if pb_space_detail:
            result = await VaccineServer().update_no_indected(account_id=pb_space_detail.owner_id,
                                                              vaccine_id=self.post_data.get("vaccine_id"),
                                                              injection_no=self.post_data.get("injection_no"),
                                                              request_id=self.request_id,
                                                              space_id=zbase62.decode(self.post_data.get('space_id')),
                                                              creator_id=self.current_user.account_id)
            rd.redis_del('injection_detail:{}'.format(zbase62.decode(self.post_data.get('space_id'))))
            pb_detail_list = await VaccineServer().get_vaccine_detail_list(request_id=self.request_id)
            pb_injection_log = await VaccineServer().get_injection_details(account_id=pb_space_detail.owner_id,
                                                                           request_id=self.request_id,
                                                                           space_id=zbase62.decode(
                                                                               self.post_data.get('space_id')),
                                                                           creator_id=self.current_user.account_id)

            inject_dict = {}
            if pb_injection_log:
                for inject in pb_injection_log.inject_detail:
                    i = InjectDetail(inject).inject_detail
                    i["date_of_inoculation"] = time.strftime("%Y-%m-%d",
                                                             time.localtime(inject.date_of_inoculation.seconds))
                    inject_dict[(i.get("vaccine_id"), i.get("injection_no"))] = i

            detail_list = []
            if pb_detail_list:
                for vaccine in pb_detail_list.vaccines:
                    v = Vaccine(vaccine).vaccine
                    vd = inject_dict.get((v.get("vaccine_id"), v.get("injection_no")))
                    v['is_injected'] = vd.get("is_injected") if vd else None
                    v['date_of_inoculation'] = vd.get("date_of_inoculation") if vd else None
                    detail_list.append(v)

            if result:
                self.send_to_client(0, message='设置成功', response=detail_list)
                return

            raise HTTPError(500, "update no inject indected failed", reason="设置失败，请联系客服解决")

        raise HTTPError(500, "get space failed", reason="服务器出错，请联系客服解决")


class UpdatePlanInject(APIHandler):
    """设置计划接种

    """

    @authenticated_async
    async def post(self):
        try:
            libs.validator.space_id(self.post_data.get('space_id'))
            libs.validator.vaccine_id(self.post_data.get('vaccine_id'))
            libs.validator.record_at(self.post_data.get('date_of_inoculation'))
            libs.validator.injection_no(self.post_data.get('injection_no'))
        except libs.validator.ValidationError as e:
            self.send_to_client(-1, message=e.__str__())
            return
        today = datetime.datetime.now().date()
        date = datetime.datetime.strptime(self.post_data.get("date_of_inoculation"), "%Y-%m-%d").date()
        if date < today:
            self.send_to_client(-1, message='计划接种日期应大于当前日期')
            return
        pb_space_detail = await SpaceServer().get_space_details(space_id=zbase62.decode(self.post_data.get('space_id')),
                                                                request_id=self.request_id)

        if pb_space_detail:
            result = await VaccineServer().update_plan_inject(account_id=pb_space_detail.owner_id,
                                                              vaccine_id=self.post_data.get("vaccine_id"),
                                                              injection_no=self.post_data.get("injection_no"),
                                                              date_of_inoculation=self.post_data.get(
                                                                  "date_of_inoculation"),
                                                              request_id=self.request_id,
                                                              space_id=zbase62.decode(self.post_data.get('space_id')),
                                                              creator_id=self.current_user.account_id)
            rd.redis_del('injection_detail:{}'.format(zbase62.decode(self.post_data.get('space_id'))))
            pb_detail_list = await VaccineServer().get_vaccine_detail_list(request_id=self.request_id)
            pb_injection_log = await VaccineServer().get_injection_details(account_id=pb_space_detail.owner_id,
                                                                           request_id=self.request_id,
                                                                           space_id=zbase62.decode(
                                                                               self.post_data.get('space_id')),
                                                                           creator_id=self.current_user.account_id)

            inject_dict = {}
            if pb_injection_log:
                for inject in pb_injection_log.inject_detail:
                    i = InjectDetail(inject).inject_detail
                    i["date_of_inoculation"] = time.strftime("%Y-%m-%d",
                                                             time.localtime(inject.date_of_inoculation.seconds))
                    inject_dict[(i.get("vaccine_id"), i.get("injection_no"))] = i

            detail_list = []
            if pb_detail_list:
                for vaccine in pb_detail_list.vaccines:
                    v = Vaccine(vaccine).vaccine
                    vd = inject_dict.get((v.get("vaccine_id"), v.get("injection_no")))
                    v['is_injected'] = vd.get("is_injected") if vd else None
                    v['date_of_inoculation'] = vd.get("date_of_inoculation") if vd else None
                    detail_list.append(v)

            if result:
                self.send_to_client(0, message='设置成功', response=detail_list)
                return

            raise HTTPError(500, "update plan inject failed", reason="设置失败，请联系客服解决")

        raise HTTPError(500, "get space failed", reason="服务器出错，请联系客服解决")


class UpdateInjected(APIHandler):
    """设置已接种

    """

    @authenticated_async
    async def post(self):
        try:
            libs.validator.space_id(self.post_data.get('space_id'))
            libs.validator.vaccine_id(self.post_data.get('vaccine_id'))
            libs.validator.record_at(self.post_data.get('date_of_inoculation'))
            libs.validator.injection_no(self.post_data.get('injection_no'))
        except libs.validator.ValidationError as e:
            self.send_to_client(-1, message=e.__str__())
            return
        pb_space_detail = await SpaceServer().get_space_details(space_id=zbase62.decode(self.post_data.get('space_id')),
                                                                request_id=self.request_id)
        if pb_space_detail:
            result = await VaccineServer().update_injected(account_id=pb_space_detail.owner_id,
                                                           vaccine_id=self.post_data.get("vaccine_id"),
                                                           injection_no=self.post_data.get("injection_no"),
                                                           date_of_inoculation=self.post_data.get(
                                                               "date_of_inoculation"),
                                                           request_id=self.request_id,
                                                           space_id=zbase62.decode(self.post_data.get('space_id')),
                                                           creator_id=self.current_user.account_id)
            rd.redis_del('injection_detail:{}'.format(zbase62.decode(self.post_data.get('space_id'))))
            pb_detail_list = await VaccineServer().get_vaccine_detail_list(request_id=self.request_id)
            pb_injection_log = await VaccineServer().get_injection_details(account_id=pb_space_detail.owner_id,
                                                                           request_id=self.request_id,
                                                                           space_id=zbase62.decode(
                                                                               self.post_data.get('space_id')),
                                                                           creator_id=self.current_user.account_id)

            inject_dict = {}
            if pb_injection_log:
                for inject in pb_injection_log.inject_detail:
                    i = InjectDetail(inject).inject_detail
                    i["date_of_inoculation"] = time.strftime("%Y-%m-%d",
                                                             time.localtime(inject.date_of_inoculation.seconds))
                    inject_dict[(i.get("vaccine_id"), i.get("injection_no"))] = i

            detail_list = []
            if pb_detail_list:
                for vaccine in pb_detail_list.vaccines:
                    v = Vaccine(vaccine).vaccine
                    vd = inject_dict.get((v.get("vaccine_id"), v.get("injection_no")))
                    v['is_injected'] = vd.get("is_injected") if vd else None
                    v['date_of_inoculation'] = vd.get("date_of_inoculation") if vd else None
                    detail_list.append(v)

            if result:
                self.send_to_client(0, message='设置成功', response=detail_list)
                return

            raise HTTPError(500, "update injected failed", reason="设置失败，请联系客服解决")

        raise HTTPError(500, "get space failed", reason="服务器出错，请联系客服解决")
