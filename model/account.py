from google.protobuf.json_format import MessageToDict

from core import backend
from libs import zbase62
from microserver.pb import pbaccount_pb2


class Account(object):
    def __init__(self, pb_account):
        self._account = MessageToDict(pb_account, including_default_value_fields=True, preserving_proto_field_name=True,
                                      use_integers_for_enums=True)

        self._account["account_id"] = pb_account.account_id
        self._account["status"] = pb_account.status

        self._userinfo = None
        self.__dict__ = self._account

    def __getattr__(self, name):
        return self.__dict__[name]

    async def set_userinfo(self, pb_userinfo):
        self.userinfo = MessageToDict(pb_userinfo, including_default_value_fields=True,
                                      preserving_proto_field_name=True,
                                      use_integers_for_enums=True)
        if pb_userinfo.avatar:
            avatar, err = await backend.backend_user_media.get_public_url(pb_userinfo.avatar)
        else:
            avatar = None
        self.userinfo['avatar'] = avatar if avatar is not None else ""

    def dump(self):
        # wechat 是否绑定
        wechat = False
        for partner in self.partner:
            if partner == 'wechat' or partner["partner"] == pbaccount_pb2.PARTNER_WECHAT:
                wechat = True

        return {
            "account_id": zbase62.encode(self.account_id),
            "auth_token": self.auth_token,
            "mobile": self.mobile.get('mobile'),
            "partner": {
                "wechat": wechat
            },
            "userinfo": self.userinfo
        }

    @classmethod
    def translate_error(cls, error):
        err_map = {
            "account error: not found": "账号不存在",
            "account error: already exists": "账号已经存在",
            "account error: password error": "密码错误",
            "account error: token error or expired": "登录过期，请重新登录",
            "account error: account is unactivated": "账号未激活",
            "account error: account is disabled": "账号已锁定",
            "account error: account was deleted": "账号已注销",
            "account error: account status unknown": "账号状态未知",
        }
        return err_map.get(error, error)


class UserInfo(object):
    def __init__(self, pb_userinfo):
        self.userinfo = MessageToDict(pb_userinfo, including_default_value_fields=True,
                                      preserving_proto_field_name=True,
                                      use_integers_for_enums=True)
        self.userinfo["dob"] = pb_userinfo.dob
