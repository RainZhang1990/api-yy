import json
import time
import arrow
import datetime

import libs.validator

from tornado.web import HTTPError
from handler.api import APIHandler
from microserver.server.record import RecordServer
from microserver.server.zid import ZIDServer
from microserver.server.feed import FeedServer
from microserver.pb import pbfeed_pb2
from core.config import Config
from core import redis as rd
from .api import authenticated_async
from model.record import GrowthDetail
from libs import zbase62


class GetGrowthList(APIHandler):
    ''' 宝宝生长记录

    '''

    @authenticated_async
    async def post(self):
        try:
            libs.validator.space_id(self.post_data.get("space_id"))
            libs.validator.account_id(self.post_data.get("account_id"))

        except libs.validator.ValidationError as e:
            self.send_to_client(-1, message=e.__str__())
            return

        growth_list_key = 'growth_list:{}'.format(zbase62.decode(self.post_data.get('space_id')))
        growth_list = rd.redis_get(growth_list_key)
        growth_list = json.loads(str(growth_list, encoding="utf-8")) if isinstance(growth_list, bytes) else growth_list
        if not growth_list:
            pb_growth_list = await RecordServer().get_growth_list(
                account_id=zbase62.decode(self.post_data.get("account_id")),
                space_id=zbase62.decode(
                    self.post_data.get('space_id')),
                creator_id=self.current_user.account_id,
                request_id=self.request_id)
            if pb_growth_list:
                growth_list = []
                for growth in pb_growth_list.growth_list:
                    growth_list.append(GrowthDetail(growth).growth_detail)
                rd.redis_set(growth_list_key, json.dumps(growth_list), Config().redis.get("expire_list"))

        if growth_list is not None:
            self.send_to_client(0, message='成功获取生长记录详情', response=growth_list)
            return

        raise HTTPError(500, "get growth list failed", reason="服务器出错，请联系客服解决")


class AddRecord(APIHandler):
    @authenticated_async
    async def post(self):
        if (self.post_data.get("height") or self.post_data.get("weight") or self.post_data.get(
                "head_circumference")) is None:
            self.send_to_client(-1, message='请至少输入一项数据')
            return

        try:
            libs.validator.space_id(self.post_data.get("space_id"))
            libs.validator.record_at(self.post_data.get("record_at"))
            if self.post_data.get("height"):
                libs.validator.height(float(self.post_data.get("height")))
            if self.post_data.get("weight"):
                libs.validator.weight(float(self.post_data.get("weight")))
            if self.post_data.get("head_circumference"):
                libs.validator.head_circumference(float(self.post_data.get("head_circumference")))

        except libs.validator.ValidationError as e:
            self.send_to_client(-1, message=e.__str__())
            return

        record_at = arrow.get(self.post_data.get('record_at'))
        record_at_utc = record_at.utcfromtimestamp(record_at.timestamp).datetime
        record_at_timestamp = record_at.timestamp
        if record_at_timestamp > time.time():
            self.send_to_client(-1, message='记录日期有误')
            return

        if self.post_data.get("height") and self.post_data.get("weight"):
            # bmi值异常检测
            if self.post_data.get("weight") / (
                    self.post_data.get("height") * self.post_data.get("height") / 10000) > 60:
                self.send_to_client(-1, message='bmi值异常, 请正确输入宝宝的体重身高信息')
                return

        is_done, message = await RecordServer().add_record(account_id=zbase62.decode(self.post_data.get("account_id")),
                                                           height=self.post_data.get("height"),
                                                           weight=self.post_data.get("weight"),
                                                           head_circumference=self.post_data.get("head_circumference"),
                                                           record_at=record_at_utc,
                                                           space_id=zbase62.decode(self.post_data.get('space_id')),
                                                           creator_id=self.current_user.account_id,
                                                           request_id=self.request_id)

        if is_done:
            rd.redis_del('growth_list:{}'.format(zbase62.decode(self.post_data.get('space_id'))))
            # to feed
            word_list = []
            if self.post_data.get("weight") is not None:
                word_list.append("体重：{}KG".format(self.post_data.get("weight")))
            if self.post_data.get("height") is not None:
                word_list.append("身高：{}CM".format(self.post_data.get("height")))
            if self.post_data.get("head_circumference") is not None:
                word_list.append("头围：{}CM".format(self.post_data.get("head_circumference")))

            feed_id = await ZIDServer().generate(self.request_id)
            if feed_id is None:
                raise HTTPError(500, "zid-server generate failed", reason="服务器出错，请联系客服解决")

            await FeedServer().create_feed(feed_id=feed_id,
                                           space_id=[zbase62.decode(self.post_data.get('space_id'))],
                                           # privacy=self.post_data.get('privacy'), #todo: 第一版本先不加权限
                                           record_at=record_at_utc,
                                           creator_id=self.current_user.account_id,
                                           word='\n'.join(word_list),
                                           feed_type=pbfeed_pb2.FEED_TYPE_GROWTH,
                                           feed_size=0,
                                           request_id=self.request_id)

            self.send_to_client(0, message='添加成功')
        else:
            self.send_to_client(-1, message=message if message else '服务器出错，请联系客服解决')


class DeleteRecord(APIHandler):
    @authenticated_async
    async def post(self):
        try:
            libs.validator.space_id(self.post_data.get("space_id"))
            libs.validator.growth_id(self.post_data.get("growth_id"))
        except libs.validator.ValidationError as e:
            self.send_to_client(-1, message=e.__str__())
            return

        is_done, message = await RecordServer().delete_record(growth_id=self.post_data.get("growth_id"),
                                                     space_id=zbase62.decode(self.post_data.get('space_id')),
                                                     creator_id=self.current_user.account_id,
                                                     request_id=self.request_id)

        if is_done:
            rd.redis_del('growth_list:{}'.format(zbase62.decode(self.post_data.get('space_id'))))
            self.send_to_client(0, message='删除成功')
        else:
            self.send_to_client(-1, message=message if message else '服务器出错，请联系客服解决')

class UpdateRecord(APIHandler):
    @authenticated_async
    async def post(self):
        if (self.post_data.get("height") or self.post_data.get("weight") or self.post_data.get(
                "head_circumference")) is None:
            self.send_to_client(-1, message='请至少输入一项数据')
            return

        try:
            libs.validator.space_id(self.post_data.get("space_id"))
            libs.validator.growth_id(self.post_data.get("growth_id"))
            libs.validator.record_at(self.post_data.get("record_at"))
            if self.post_data.get("height"):
                libs.validator.height(float(self.post_data.get("height")))
            if self.post_data.get("weight"):
                libs.validator.weight(float(self.post_data.get("weight")))
            if self.post_data.get("head_circumference"):
                libs.validator.head_circumference(float(self.post_data.get("head_circumference")))

        except libs.validator.ValidationError as e:
            self.send_to_client(-1, message=e.__str__())
            return
        record_at = arrow.get(self.post_data.get('record_at'))
        record_at_utc = record_at.utcfromtimestamp(record_at.timestamp).datetime
        if bool(self.post_data.get("height") and self.post_data.get("weight")):
            # bmi值异常检测
            if self.post_data.get("weight") / (
                    self.post_data.get("height") * self.post_data.get("height") / 10000) > 60:
                self.send_to_client(-1, message='bmi值异常, 请正确输入宝宝的体重身高信息')
                return

        is_done, message = await RecordServer().update_record(growth_id=self.post_data.get("growth_id"),
                                                     height=self.post_data.get("height"),
                                                     weight=self.post_data.get("weight"),
                                                     head_circumference=self.post_data.get("head_circumference"),
                                                     record_at=record_at_utc,
                                                     space_id=zbase62.decode(self.post_data.get('space_id')),
                                                     creator_id=self.current_user.account_id,
                                                     request_id=self.request_id)

        if is_done:
            rd.redis_del('growth_list:{}'.format(zbase62.decode(self.post_data.get('space_id'))))
            self.send_to_client(0, message='修改成功')
        else:
            self.send_to_client(-1, message=message if message else '服务器出错，请联系客服解决')

