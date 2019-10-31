import logging

import grpc
from google.protobuf.struct_pb2 import Struct
from tornado.web import HTTPError

from core.singleton import Singleton
from microserver.mserver import MServer
from microserver.pb import pbaccount_pb2
from model.account import Account


class AccountServer(metaclass=Singleton):

    def handler_exception(self, e, tranlate_codes):
        tranlate_codes = [c.upper() for c in tranlate_codes]

        codes_httpcode_map = {
            "NOTFOUND": 404,
            "UNAUTHENTICATED": 403,
        }

        if e.code().name in tranlate_codes:
            raise HTTPError(codes_httpcode_map[e.code().name], reason=Account.translate_error(e.details()))
        else:
            raise e

    async def auth_with_token(self, token, app_id, request_id=None):
        """通过Token进行Account认证

        Returns:
            pb_account.Account -- Account信息
        """

        try:
            msg = pbaccount_pb2.AuthAccountTokenRequest()
            msg.auth_token = token
            msg.app_id = app_id

            pb_account = await MServer().call("account-server", "AuthAccountToken", msg, request_id)

            return pb_account

        except grpc.RpcError as e:
            # except grpc._channel._Rendezvous as e:
            msg = "auth token except. code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def get_account_by_id(self, account_id, app_id, request_id=None):
        """通过account_id获得Account信息

        Returns:
            pb_account.Account -- Account信息
        """

        try:
            pb_account_request = pbaccount_pb2.AccountRequest(account_id=account_id)
            msg = pbaccount_pb2.GetAccountRequest(account_request=pb_account_request, app_id=app_id)

            pb_account = await MServer().call("account-server", "GetAccount", msg, request_id)

            return pb_account

        except grpc.RpcError as e:
            msg = "get account by id except. code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def get_account_by_mobile(self, mobile, country_code="86", app_id=None, request_id=None):
        """通过mobile获得Account信息

        注意，app_id参数一定要传入，不能使用默认的None

        Returns:
            pb_account.Account -- Account信息
        """

        # check app_id first, because the app_id params have a default value with None.
        #  Maybe someone will forget to give it a value
        if app_id is None:
            raise Exception("app id empty?")

        try:
            pb_mobile = pbaccount_pb2.Mobile(country_code=country_code, mobile=mobile)
            pb_account_request = pbaccount_pb2.AccountRequest(mobile=pb_mobile)
            msg = pbaccount_pb2.GetAccountRequest(account_request=pb_account_request, app_id=app_id)

            pb_account = await MServer().call("account-server", "GetAccount", msg, request_id)

            return pb_account

        except grpc.RpcError as e:
            msg = "get account by mobile except. code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def exists_account_by_mobile(self, mobile, country_code="86", request_id=None):
        """检查是否已存在账号（mobile）

        Returns:
            pb_account.Account -- Account信息
        """

        pb_mobile = pbaccount_pb2.Mobile(country_code=country_code, mobile=mobile)
        msg = pbaccount_pb2.AccountRequest(mobile=pb_mobile)

        exists_result = await MServer().call("account-server", "ExistsAccount", msg, request_id)

        return exists_result.exists

    async def create_account(self, username=None, mobile=None, country_code="86", email=None,
                             password=None, app_id=None, request_id=None):
        """创建新账号

        注意，app_id参数一定要传入，不能使用默认的None

        Returns:
            pb_account.Account -- Account信息
        """

        # check app_id first, because the app_id params have a default value with None.
        #  Maybe someone will forget to give it a value
        if app_id is None:
            raise Exception("app id empty?")

        try:
            pb_mobile = None
            if mobile:
                pb_mobile = pbaccount_pb2.Mobile(country_code=country_code, mobile=mobile)

            msg = pbaccount_pb2.AccountCreateRequest(
                username=username, mobile=pb_mobile, email=email, password=password,
                app_id=app_id)
            pb_account = await MServer().call(
                "account-server", "CreateAccount", msg, request_id)

            return pb_account

        except grpc.RpcError as e:
            msg = "create account except. code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

            return None

    async def create_account_by_partner(self, partner, identifier, origin_data, app_id=None, request_id=None):
        """通过第三方账号创建新账号

        注意，app_id参数一定要传入，不能使用默认的None

        Returns:
            pb_account.Account -- Account信息
        """

        # check app_id first, because the app_id params have a default value with None.
        #  Maybe someone will forget to give it a value
        if app_id is None:
            raise Exception("app id empty?")

        if origin_data is None:
            origin_data = {}
        data = Struct()
        data.update(origin_data)

        msg = pbaccount_pb2.CreateAccountByPartnerAccountRequest(
            partner=partner,
            identifier=identifier,
            origin_data=data,
            app_id=app_id)
        pb_account = await MServer().call(
            "account-server", "CreateAccountByPartnerAccount", msg, request_id)

        return pb_account

    async def active_account(self, account_id, details, request_id=None):
        """激活账号: 账号状态更新

        :param account_id:
        :param details:
        :param request_id:
        :return:
        """

        pbaccount_id = pbaccount_pb2.AccountRequest(account_id=account_id)
        account_status_request = pbaccount_pb2.AccountStatusRequest(
            account_request=pbaccount_id, status=pbaccount_pb2.STATUS_ACTIVATED, details=details)
        await MServer().call(
            "account-server", "UpdateAccountStatus", account_status_request, request_id)

    async def get_userinfo(self, account_id, app_id, request_id=None):
        """获得用户信息

        Returns:
            pb_account.UserInfo -- 用户基础信息
        """

        msg = pbaccount_pb2.UserInfoRequest(account_id=account_id, app_id=app_id)
        msg.account_id = account_id
        msg.app_id = app_id

        pb_userinfo = await MServer().call("account-server", "GetUserInfo", msg, request_id)

        return pb_userinfo

    async def exists_partner_wechat(self, identifier, app_id, request_id):
        """是否存在第三方微信账号

        :param identifier:
        :param app_id:
        :return:
        """
        if app_id is None:
            raise Exception("app id empty?")

        msg = pbaccount_pb2.PartnerAccountRequest(partner=pbaccount_pb2.PARTNER_WECHAT, identifier=identifier,
                                                  app_id=app_id)
        exists_result = await MServer().call("account-server", "ExistsPartnerAccount", msg, request_id)
        return exists_result.exists

    async def auth_partner_account(self, identifier, partner=pbaccount_pb2.PARTNER_WECHAT, auto_authorize=True,
                                   app_id=None,
                                   request_id=None):
        """通过第三方账号进行认证

        注意，app_id参数一定要传入，不能使用默认的None

        :param identifier:
        :param app_id:
        :param request_id:
        :param partner:
        :param auto_authorize:
        :return:
        """
        # check app_id first, because the app_id params have a default value with None.
        #  Maybe someone will forget to give it a value
        if app_id is None:
            raise Exception("app id empty?")

        try:
            msg = pbaccount_pb2.PartnerAccountAuthRequest(partner=partner,
                                                          identifier=identifier, app_id=app_id,
                                                          auto_authorize=auto_authorize)
            pb_account = await MServer().call(
                "account-server", "AuthPartnerAccount", msg, request_id)
            return pb_account
        except grpc.RpcError as e:
            self.handler_exception(e, ["NotFound", "Unauthenticated"])

    async def bind_partner_account(self, identifier, token, origin_data, partner=pbaccount_pb2.PARTNER_WECHAT,
                                   app_id=None,
                                   request_id=None):
        """绑定第三方账号

        注意，app_id参数一定要传入，不能使用默认的None

        :param identifier:
        :param token:
        :param origin_data:
        :param app_id:
        :param request_id:
        :param partner:
        :return:
        """
        # check app_id first, because the app_id params have a default value with None.
        #  Maybe someone will forget to give it a value
        if app_id is None:
            raise Exception("app id empty?")

        info = Struct()
        info.update(origin_data)

        msg = pbaccount_pb2.PartnerAccountBindRequest(partner=partner,
                                                      auth_token=token,
                                                      identifier=identifier, origin_data=info,
                                                      app_id=app_id)
        await MServer().call(
            "account-server", "PartnerAccountBind", msg, request_id)



    async def update_partner_account_origin_data(self, auth_token, partner, identifier, origin_data, app_id,
                                                 request_id=None):
        """
        修改第三方账号的origin_data
        :param auth_token:
        :param partner:
        :param identifier:
        :param origin_data:
        :param app_id:
        :param request_id:
        :return:
        """
        if app_id is None:
            raise Exception("app id empty?")
        if origin_data is None:
            origin_data = {}

        data = Struct()
        data.update(origin_data)
        msg = pbaccount_pb2.PartnerAccountUpdateOriginDataRequest(auth_token=auth_token, partner=partner,
                                                                  identifier=identifier,
                                                                  origin_data=data,
                                                                  app_id=app_id)

        await MServer().call("account-server", "UpdatePartnerAccountOriginData", msg, request_id)

    async def update_user_info(self, account_id, params, app_id, request_id):
        """更新用户信息
        :param account_id:
        :param params:
        :param app_id:
        :param request_id:
        :return:
        """
        try:
            msg = pbaccount_pb2.UserInfoUpdateRequest(account_id=account_id,
                                                      params=params,
                                                      app_id=app_id)
            await MServer().call("account-server", "UpdateUserInfo", msg, request_id)

        except grpc.RpcError as e:
            # except grpc._channel._Rendezvous as e:
            msg = "update user info except. code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

    async def update_user_avatar(self, account_id, avatar, app_id, request_id=None):
        """更新用户头像
        :param account_id:
        :param avatar:
        :param app_id:
        :param request_id:
        :return:
        """
        try:
            msg = pbaccount_pb2.UserAvatarUpdateRequest(account_id=account_id, avatar=avatar, app_id=app_id)
            await MServer().call("account-server", "UpdateUserAvatar", msg, request_id)

        except grpc.RpcError as e:
            # except grpc._channel._Rendezvous as e:
            msg = "update user avatar except. code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)

    async def update_user_dob(self, dob, account_id, stage, app_id, request_id=None):
        """更新 DOB
        :param dob:
        :param account_id:
        :param stage:
        :param app_id:
        :param request_id:
        :return:
        """
        try:
            msg = pbaccount_pb2.UserDOBUpdateRequest(account_id=account_id, dob=dob, stage=stage, app_id=app_id)
            await MServer().call("account-server", "UpdateUserDOB", msg, request_id)
        except grpc.RpcError as e:
            # except grpc._channel._Rendezvous as e:
            msg = "update user dob except. code: {}, details:{}".format(e.code(), e.details())
            logging.warning(msg)
