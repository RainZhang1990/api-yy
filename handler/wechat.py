from google.protobuf.json_format import MessageToDict
from tornado.web import HTTPError

from core import backend
from core.config import Config
from handler.api import APIHandler, authenticated_async
from microserver.pb import pbaccount_pb2
from microserver.server.account import AccountServer
from microserver.server.membership import MembershipServer
from microserver.server.wxcc import WxCCServer
from microserver.server.zid import ZIDServer
from model.account import Account


class MiniProgramLoginHandler(APIHandler):
    async def post(self):
        code = self.post_data.get('code', None)
        if not code:
            raise HTTPError(400, "code为空？", reason="code为空？")

        # login to fetch openid/session_key/unionid
        login_response = await WxCCServer().miniprogram_login(code, self.request_id)
        if login_response is None:
            raise HTTPError(500, "登录微信服务器出错", reason="登录微信服务器出错")

        # get account
        exists_wechat = await AccountServer().exists_partner_wechat(identifier=login_response.unionid,
                                                                    app_id=self.app_id_int64,
                                                                    request_id=self.request_id)

        if not exists_wechat:
            # create account
            pb_account = await AccountServer().create_account_by_partner(partner=pbaccount_pb2.PARTNER_WECHAT,
                                                                         identifier=login_response.unionid,
                                                                         origin_data={},
                                                                         app_id=self.app_id_int64,
                                                                         request_id=self.request_id)
            # 分配空间
            await MembershipServer().set_total_storage_change(
                account_id=pb_account.account_id,
                changed_value=Config().membership.get("register_default_size"),
                title=Config().membership.get("register_default_title"),
                details=Config().membership.get("register_default_details"),
                request_id=self.request_id)
        else:
            pb_account = await AccountServer().auth_partner_account(identifier=login_response.unionid,
                                                                    app_id=self.app_id_int64,
                                                                    request_id=self.request_id)

            # set account pair to wxcc server
        await WxCCServer().miniprogram_set_account_pair(account_id=pb_account.account_id,
                                                        login_response=login_response,
                                                        request_id=self.request_id)

        account = Account(pb_account)
        pb_userinfo = await AccountServer().get_userinfo(account.account_id, app_id=self.app_id_int64,
                                                         request_id=self.request_id)
        await account.set_userinfo(pb_userinfo)

        self.send_to_client(0, message='登录成功', response=account.dump())


class MiniProgramUpdateUserinfoHandler(APIHandler):
    @authenticated_async
    async def post(self):
        # decrypt userinfo
        userinfo = await WxCCServer().miniprogram_decrypt_userinfo(self.current_user.account_id,
                                                                   self.post_data.get("rawData"),
                                                                   self.post_data.get("encryptedData"),
                                                                   self.post_data.get("signature"),
                                                                   self.post_data.get("iv"), self.request_id)
        userinfo_dict = MessageToDict(userinfo, including_default_value_fields=True, preserving_proto_field_name=True,
                                      use_integers_for_enums=True)

        # update partner info
        await AccountServer().update_partner_account_origin_data(self.token,
                                                                 pbaccount_pb2.PARTNER_WECHAT,
                                                                 userinfo.unionid,
                                                                 userinfo_dict,
                                                                 self.app_id_int64,
                                                                 self.request_id)

        # get userinfo
        pb_current_userinfo = await AccountServer().get_userinfo(self.current_user.account_id, self.app_id_int64,
                                                                 self.request_id)

        # update user info
        params_people = dict()
        if not pb_current_userinfo.nickname:
            params_people["nickname"] = userinfo.nickname
        if not pb_current_userinfo.gender:
            params_people["gender"] = str(userinfo.gender)
        if params_people:
            await AccountServer().update_user_info(account_id=self.current_user.account_id, params=params_people,
                                                   app_id=self.app_id_int64,
                                                   request_id=self.request_id)

        if not pb_current_userinfo.avatar:
            # generate avatar filename
            zid = await ZIDServer().generate(self.request_id)

            # upload
            filename, err = await backend.backend_user_media.transmit_wechat_avatar(zid=zid,
                                                                                    remote_url=userinfo.avatar)
            if not err and filename:
                # update avatar
                await AccountServer().update_user_avatar(account_id=self.current_user.account_id,
                                                         app_id=self.app_id_int64,
                                                         request_id=self.request_id, avatar=filename)

        pb_userinfo = await AccountServer().get_userinfo(self.current_user.account_id, self.app_id_int64,
                                                         self.request_id)
        await self.current_user.set_userinfo(pb_userinfo)

        self.send_to_client(0, response=self.current_user.dump())
