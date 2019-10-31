from core.config import Config
from core.singleton import Singleton
from microserver.mserver import MServer
from microserver.pb import pbwxcc_pb2


class WxCCServer(metaclass=Singleton):
    # mini program---------------------------------------------------------------------------------
    async def miniprogram_login(self, code, request_id=None):
        """
        小程序登录微信服务器
        :param code:
        :param request_id:
        :return: pbwxcc_pb2.MiniProgramLoginResponse
        """
        msg = pbwxcc_pb2.MiniProgramLoginRequest()
        msg.appid = Config().wx_app_id.get("miniprogram")
        msg.code = code

        pb_response = await MServer().call("wxcc-server", "MiniProgramLogin", msg, request_id)

        return pb_response

    async def miniprogram_set_account_pair(self, account_id, login_response, request_id=None):
        """
        保存account_id与LoginResponse的匹配项
        :param account_id:
        :param login_response: miniprogram_login返回的response
        :param request_id:
        :return: None
        """

        msg = pbwxcc_pb2.MiniProgramSetAccountPairRequest(appid=Config().wx_app_id.get("miniprogram"),
                                                          account_id=account_id, login_response=login_response)

        await MServer().call("wxcc-server", "MiniProgramSetAccountPair", msg, request_id)

    async def miniprogram_decrypt_userinfo(self, account_id, raw_data, encrypted_data, signature, iv, request_id=None):
        """
        解密userinfo
        :param account_id:
        :param raw_data:
        :param encrypted_data:
        :param signature:
        :param iv:
        :param request_id:
        :return:
        """
        msg = pbwxcc_pb2.EncryptedUserinfo(appid=Config().wx_app_id.get("miniprogram"), account_id=account_id,
                                           raw_data=raw_data,
                                           encrypted_data=encrypted_data,
                                           signature=signature, iv=iv)

        return await MServer().call("wxcc-server", "MiniProgramDecryptUserInfo", msg, request_id)

    # open app---------------------------------------------------------------------------------

    async def open_app_login(self, code, request_id=None):
        """
        开放平台APP登录微信服务器
        :param code:
        :param request_id:
        :return: pbwxcc_pb2.Userinfo
        """
        msg = pbwxcc_pb2.OpenAppLoginRequest()
        msg.appid = Config().wx_app_id.get("open_app")
        msg.code = code

        pb_response = await MServer().call("wxcc-server", "OpenAppLogin", msg, request_id)

        return pb_response

    async def open_app_set_account_pair(self, openid, account_id, request_id=None):
        """
        设置account_id与appid及open_id的匹配
        :param code:
        :param request_id:
        :return: pbwxcc_pb2.Userinfo
        """
        msg = pbwxcc_pb2.OpenAppSetAccountPairRequest()
        msg.appid = Config().wx_app_id.get("open_app")
        msg.openid = openid
        msg.account_id = account_id

        pb_response = await MServer().call("wxcc-server", "OpenAppSetAccountPair", msg, request_id)

        return pb_response