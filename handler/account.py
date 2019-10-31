import datetime
import os
import re
import uuid

import grpc
from google.protobuf.json_format import MessageToDict
from tornado.web import HTTPError

import libs.validator
from core import backend, error
from core import redis as rd
from core.config import Config
from microserver.mserver import MServer
from microserver.pb import pbaccount_pb2
from microserver.server.account import AccountServer
from microserver.server.membership import MembershipServer
from microserver.server.wxcc import WxCCServer
from microserver.server.zid import ZIDServer
from model.account import Account
from .api import APIHandler, authenticated_async


class LoginPasswordHandler(APIHandler):
    ''' 仅用于审核

    '''

    async def post(self):
        username = self.post_data.get('username', '')
        password = self.post_data.get('password', '')
        try:
            libs.validator.username(username)
            libs.validator.password(password)
        except libs.validator.ValidationError as e:
            self.send_to_client(-1, message=e.__str__())
            return
        if username == Config().password_login.get('username') and password == Config().password_login.get('password'):
            pb_account = await AccountServer().get_account_by_id(
                account_id=int(Config().password_login.get('account_id')),
                app_id=self.app_id_int64,
                request_id=self.request_id)

            account = Account(pb_account)
            # get account userinfo
            if account.status == pbaccount_pb2.STATUS_ACTIVATED:
                pb_userinfo = await AccountServer().get_userinfo(account.account_id, app_id=self.app_id_int64,
                                                                 request_id=self.request_id)
                await account.set_userinfo(pb_userinfo)
                self.send_to_client(0, message='登陆成功', response=account.dump())
            else:
                self.send_to_client(-1, message='登录状态异常')

        else:
            self.send_to_client(-1, message='账号或密码错误')


class LoginMobileHandler(APIHandler):
    '''
    手机号登录
    '''

    async def post(self):
        mobile = self.post_data.get('mobile', '')
        smscode = self.post_data.get('smscode', '')

        errors = self._check_input({"mobile": mobile, "smscode": smscode})
        if errors:
            err = ''
            for item, er in errors.items():
                err = er
                break
            self.send_to_client(error_id=error.input_error.id, message=err)
            return

        # Check smscode
        mobile_smscode = rd.redis_get('verify:{}'.format(mobile))

        if mobile_smscode:
            mobile_smscode = mobile_smscode.decode()

        if mobile_smscode != smscode:
            self.send_to_client(-1, '登陆验证码错误')
            return

        # Exists Mobile
        exists_account_already = False
        try:
            exists_account_already = await AccountServer().exists_account_by_mobile(mobile, request_id=self.request_id)
        except grpc.RpcError as e:
            self.send_to_client(error_id=500, message='服务器内部错误，请联系管理员确认')
            return

        pb_account = None
        if not exists_account_already:
            # not exists, create account
            pb_account = await AccountServer().create_account(mobile=mobile, country_code="86",
                                                              app_id=self.app_id_int64,
                                                              request_id=self.request_id)
            # 分配空间
            result = await MembershipServer().set_total_storage_change(account_id=pb_account.account_id,
                                                                       changed_value=Config().membership.get(
                                                                           "register_default_size"),
                                                                       title=Config().membership.get(
                                                                           "register_default_title"),
                                                                       details=Config().membership.get(
                                                                           "register_default_details"),
                                                                       request_id=self.request_id)

        else:
            # exists, get the account
            pb_account = await AccountServer().get_account_by_mobile(mobile=mobile, country_code="86",
                                                                     app_id=self.app_id_int64,
                                                                     request_id=self.request_id)

        # make Account Model
        if pb_account is None:
            self.send_to_client(error_id=500, message='服务器内部错误，请联系管理员确认')
            return
        account = Account(pb_account)

        # get account userinfo
        if account.status == pbaccount_pb2.STATUS_ACTIVATED:
            rd.redis_del('verify:{}'.format(mobile))
            pb_userinfo = await AccountServer().get_userinfo(account.account_id, app_id=self.app_id_int64,
                                                             request_id=self.request_id)
            await account.set_userinfo(pb_userinfo)
            self.send_to_client(0, message='登陆成功', response=account.dump())
            return

        status_error = {0: "未知状态的账号", 2: "未激活账号", 3: "锁定并暂停账号或封号", 4: "账号已注销"}
        self.send_to_client(-1, message=status_error.get(account.status))

    def _check_input(self, info):
        mobile = info.get('mobile')
        smscode = info.get('smscode')
        errors = {}
        try:
            libs.validator.mobile(mobile)
        except libs.validator.ValidationError as e:
            errors['mobile'] = e.__str__()

        try:
            libs.validator.smscode(smscode)
        except libs.validator.ValidationError as e:
            errors['mobile'] = e.__str__()

        return errors


class LoginWechatHandler(APIHandler):
    '''
    微信登录
    '''

    async def post(self):
        code = self.post_data.get('code', None)
        if not code:
            raise HTTPError(400, "code为空？", reason="code为空？")

        # fetch userinfo from wechat server
        wx_pb_userinfo = await WxCCServer().open_app_login(code, self.request_id)
        if wx_pb_userinfo is None:
            raise HTTPError(500, "登录微信服务器出错", reason="登录微信服务器出错")

        wx_userinfo_dict = MessageToDict(wx_pb_userinfo, including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

        # get account
        exists_wechat = await AccountServer().exists_partner_wechat(identifier=wx_pb_userinfo.unionid,
                                                                    app_id=self.app_id_int64,
                                                                    request_id=self.request_id)
        if not exists_wechat:
            # create account
            pb_account = await AccountServer().create_account_by_partner(partner=pbaccount_pb2.PARTNER_WECHAT,
                                                                         identifier=wx_pb_userinfo.unionid,
                                                                         origin_data=wx_userinfo_dict,
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
            # auth the wechat account
            pb_account = await AccountServer().auth_partner_account(wx_pb_userinfo.unionid,
                                                                    app_id=self.app_id_int64,
                                                                    request_id=self.request_id)

            # update partner info
            await AccountServer().update_partner_account_origin_data(pb_account.auth_token,
                                                                     pbaccount_pb2.PARTNER_WECHAT,
                                                                     wx_pb_userinfo.unionid,
                                                                     wx_userinfo_dict,
                                                                     self.app_id_int64,
                                                                     self.request_id)

        # set account pair to wxcc server
        await WxCCServer().open_app_set_account_pair(openid=wx_pb_userinfo.openid,
                                                     account_id=pb_account.account_id,
                                                     request_id=self.request_id)

        # get userinfo
        pb_current_userinfo = await AccountServer().get_userinfo(pb_account.account_id, self.app_id_int64,
                                                                 self.request_id)

        # update user info
        params_people = dict()
        if not pb_current_userinfo.nickname:
            params_people["nickname"] = wx_pb_userinfo.nickname
        if not pb_current_userinfo.gender:
            params_people["gender"] = str(wx_pb_userinfo.gender)
        if params_people:
            await AccountServer().update_user_info(account_id=pb_account.account_id,
                                                   params=params_people,
                                                   app_id=self.app_id_int64,
                                                   request_id=self.request_id)

        if not pb_current_userinfo.avatar:
            # generate avatar filename
            zid = await ZIDServer().generate(self.request_id)

            # upload
            filename, err = await backend.backend_user_media.transmit_wechat_avatar(zid=zid,
                                                                                    remote_url=wx_pb_userinfo.avatar)
            if not err and filename:
                # update avatar
                await AccountServer().update_user_avatar(account_id=pb_account.account_id,
                                                         app_id=self.app_id_int64,
                                                         request_id=self.request_id, avatar=filename)

        account = Account(pb_account)
        pb_userinfo = await AccountServer().get_userinfo(pb_account.account_id, self.app_id_int64,
                                                         self.request_id)
        await account.set_userinfo(pb_userinfo)

        self.send_to_client(0, message='登录成功', response=account.dump())


class UpdateInfoHandler(APIHandler):
    '''
    基本信息修改: 
    '''

    @authenticated_async
    async def post(self):
        allow_set = {"name", "nickname", "gender"}
        params_people = {}
        for k in set(self.post_data.keys()).intersection(allow_set):
            params_people[k] = self.post_data.get(k)
        if self.post_data.get("name"):
            try:
                libs.validator.nickname(self.post_data.get("name"))
            except libs.validator.ValidationError as e:
                self.send_to_client(-1, message=e.__str__())
                return
        if self.post_data.get("nickname"):
            try:
                libs.validator.nickname(self.post_data.get("nickname"))
            except libs.validator.ValidationError as e:
                self.send_to_client(-1, message=e.__str__())
                return
        if self.post_data.get("dob"):
            try:
                libs.validator.dob(self.post_data.get("dob"))
            except libs.validator.ValidationError as e:
                self.send_to_client(-1, message=e.__str__())
                return
        try:
            if params_people:
                await AccountServer().update_user_info(account_id=self.current_user.account_id, params=params_people,
                                                       app_id=self.app_id_int64, request_id=self.request_id)
            if self.post_data.get("dob"):
                today = datetime.datetime.now().date()
                date = datetime.datetime.strptime(self.post_data.get("dob"), "%Y-%m-%d").date()
                if date > today:
                    self.send_to_client(-1, message='生日应小于当前日期')
                    return
                await AccountServer().update_user_dob(dob=self.post_data.get("dob"),
                                                      account_id=self.current_user.account_id,
                                                      stage=self.post_data.get("stage"), app_id=self.app_id_int64,
                                                      request_id=self.request_id)

            pb_userinfo = await AccountServer().get_userinfo(account_id=self.current_user.account_id,
                                                             app_id=self.app_id_int64,
                                                             request_id=self.request_id)
            if pb_userinfo:
                account = self.current_user
                await account.set_userinfo(pb_userinfo)
                self.send_to_client(0, message='修改成功', response=account.dump())
                return

            raise HTTPError(500, "get userinfo failed", reason="服务器出错，请联系客服解决")

        except grpc.RpcError as e:
            # except grpc._channel._Rendezvous as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            raise HTTPError(500, msg, reason=str(e.details()))


class UpdateAvatarHandler(APIHandler):
    '''
    头像修改
    '''

    @authenticated_async
    async def post(self):
        try:
            # upload file
            avatar_files = self.request.files.get('file')
            if not avatar_files:
                self.send_to_client(error_id=400, message='请上传头像')
                return
            avatar_file = avatar_files[0]

            # save to temp file
            tempfile = Config().uploads_temp_path + str(uuid.uuid4())
            fh = open(tempfile, 'wb')
            fh.write(avatar_file.get('body'))
            fh.close()

            # upload
            zid = await ZIDServer().generate(self.request_id)
            filename, err = await backend.backend_user_media.upload_avatar(zid, tempfile, "square")

            # remove temp file
            try:
                os.remove(tempfile)
            except:
                pass

            if err:
                self.send_to_client(error_id=500, message='头像上传失败。错误信息：' + err)
                return

            if not filename:
                self.send_to_client(error_id=500, message='头像上传失败（未知错误），请联系管理员解决')
                return

            # 更新记录
            pb_userinfo = await AccountServer().get_userinfo(account_id=self.current_user.account_id,
                                                             app_id=self.app_id_int64,
                                                             request_id=self.request_id)
            # 删除原头像
            if pb_userinfo:
                if pb_userinfo.avatar:
                    await backend.backend_user_media.delete_object(pb_userinfo.avatar)
            pb_userinfo.avatar = filename
            # update avatar
            await AccountServer().update_user_avatar(account_id=self.current_user.account_id, app_id=self.app_id_int64,
                                                     request_id=self.request_id, avatar=filename)
            account = self.current_user
            await account.set_userinfo(pb_userinfo)
            self.send_to_client(0, message='头像上传成功', response=account.dump())
            return

        except grpc.RpcError as e:
            # except grpc._channel._Rendezvous as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            raise HTTPError(500, msg, reason=str(e.details()))


class BindMobileHandler(APIHandler):
    '''
    手机号绑定及修改
    '''

    @authenticated_async
    async def post(self):
        mobile = self.post_data.get('mobile', '').strip()
        smscode = self.post_data.get('smscode', '').strip()

        errors = self._check_input({"mobile": mobile, "smscode": smscode})
        if errors:
            err = ''
            for item, er in errors.items():
                err = er
                break
            self.send_to_client(error_id=error.input_error.id, message=err, response=errors)
            return

        # Check smscode
        mobile_smscode = rd.redis_get('verify:{}'.format(mobile))

        if mobile_smscode:
            mobile_smscode = mobile_smscode.decode()

        if mobile_smscode != smscode:
            self.send_to_client(-1, '验证码错误')
            return

        try:
            mobile_new = pbaccount_pb2.Mobile(country_code="86", mobile=mobile)
            msg = pbaccount_pb2.AccountUpdateRequest(
                auth_token=self.token, mobile_new=mobile_new, app_id=self.app_id_int64)
            await MServer().call(
                "account-server", "Update", msg, self.request_id)

            pb_userinfo = await AccountServer().get_userinfo(account_id=self.current_user.account_id,
                                                             app_id=self.app_id_int64,
                                                             request_id=self.request_id)
            if pb_userinfo:
                account = self.current_user
                await account.set_userinfo(pb_userinfo)
                self.send_to_client(0, message='修改成功', response=account.dump())
                return

            raise HTTPError(500, "get userinfo failed", reason="服务器出错，请联系客服解决")

        except grpc.RpcError as e:
            # except grpc._channel._Rendezvous as e:
            msg = "code: {}, details:{}".format(e.code(), e.details())
            if e.code().__dict__.get('_name_') == 'ALREADY_EXISTS':
                raise HTTPError(-1, "mobile already exists", reason="该手机号已存在！")
            raise HTTPError(500, msg, reason=str(e.details()))

    def _check_input(self, info):
        mobile = info.get('mobile')
        smscode = info.get('smscode')
        errors = {}
        try:
            libs.validator.mobile(mobile)
        except libs.validator.ValidationError as e:
            errors['mobile'] = e.__str__()

        try:
            libs.validator.smscode(smscode)
        except libs.validator.ValidationError as e:
            errors['mobile'] = e.__str__()

        return errors


class BindWechatHandler(APIHandler):
    '''
    微信绑定
    '''

    @authenticated_async
    async def post(self):
        code = self.post_data.get('code', None)
        if not code:
            raise HTTPError(400, "code为空？", reason="code为空？")

        # fetch userinfo from wechat server
        wx_pb_userinfo = await WxCCServer().open_app_login(code, self.request_id)
        if wx_pb_userinfo is None:
            raise HTTPError(500, "登录微信服务器出错", reason="登录微信服务器出错")

        wx_userinfo_dict = MessageToDict(wx_pb_userinfo, including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

        # bind
        await AccountServer().bind_partner_account(identifier=wx_pb_userinfo.unionid,
                                                   token=self.token,
                                                   origin_data=wx_userinfo_dict, app_id=self.app_id_int64)

        # set account pair to wxcc server
        await WxCCServer().open_app_set_account_pair(openid=wx_pb_userinfo.openid,
                                                     account_id=self.current_user.account_id,
                                                     request_id=self.request_id)

        # get userinfo
        pb_current_userinfo = await AccountServer().get_userinfo(self.current_user.account_id, self.app_id_int64,
                                                                 self.request_id)

        # update user info
        params_people = dict()
        if not pb_current_userinfo.nickname:
            params_people["nickname"] = wx_pb_userinfo.nickname
        if not pb_current_userinfo.gender:
            params_people["gender"] = str(wx_pb_userinfo.gender)
        if params_people:
            await AccountServer().update_user_info(account_id=self.current_user.account_id,
                                                   params=params_people,
                                                   app_id=self.app_id_int64,
                                                   request_id=self.request_id)

        if not pb_current_userinfo.avatar:
            # generate avatar filename
            zid = await ZIDServer().generate(self.request_id)

            # upload
            filename, err = await backend.backend_user_media.transmit_wechat_avatar(zid=zid,
                                                                                    remote_url=wx_pb_userinfo.avatar)
            if not err and filename:
                # update avatar
                await AccountServer().update_user_avatar(account_id=self.current_user.account_id,
                                                         app_id=self.app_id_int64,
                                                         request_id=self.request_id, avatar=filename)

        account = self.current_user
        account.partner = {"wechat": True}
        pb_userinfo = await AccountServer().get_userinfo(self.current_user.account_id, self.app_id_int64,
                                                         self.request_id)
        await account.set_userinfo(pb_userinfo)

        self.send_to_client(0, message='绑定', response=account.dump())


class TokenAuthHandler(APIHandler):
    """token 验证
    """

    @authenticated_async
    async def post(self):
        pb_userinfo = await AccountServer().get_userinfo(self.current_user.account_id, app_id=self.app_id_int64,
                                                         request_id=self.request_id)
        if pb_userinfo:
            account = self.current_user
            await account.set_userinfo(pb_userinfo)
            self.send_to_client(0, message='登陆成功', response=account.dump())
