import base64
import functools
import hashlib
import logging
import math
import json
import uuid
from concurrent.futures import ThreadPoolExecutor
from distutils.version import LooseVersion as V

from tornado import gen
from tornado.escape import json_decode, json_encode
from tornado.web import HTTPError, RequestHandler

from core.config import Config
# from core.server_status import get_server_status
# from microserver.pb import pbaccount_pb2
# from microserver.server.account import AccountServer
# from model.account import Account


def authenticated_async(method):
    """Decorate methods with this to require that the user be logged in.
    """

    @functools.wraps(method)
    async def wrapper(self, *args, **kwargs):
        if not self.token==self.secret:
            raise HTTPError(401, "token mismatch", reason="token mismatch")
        await method(self, *args, **kwargs)

    return wrapper


class APIHandler(RequestHandler):
    executor = ThreadPoolExecutor()

    def __init__(self, application, request, **kwargs):
        super(APIHandler, self).__init__(application, request, **kwargs)

        self.app_id = None
        self.app_id_int64 = None
        self.app_version = None

        self.post_data = None
        self.token = None
        self.secret = None
        self.params = {}


    def set_default_headers(self):
        self.set_header('Server', 'YYServer')
        self.set_header('Access-Control-Allow-Origin', '*')


    def options(self):
        # no body
        # 对于一些提交到服务器处理的数据，只需要返回是否成功的情况下，
        # 可以考虑使用状态码204（也就是XMLHttpRequest.status）来作为返回信息，
        # 从而省掉多余的数据传输
        self.set_status(204)
        self.finish()

    # async def get_current_user_async(self) -> Account:
    #     if not self.token:
    #         return None
    #
    #     token_key = "app:{}_token:{}".format(self.app_id_int64, self.token)
    #     account_cache = rd.redis_get(token_key)
    #     if account_cache:
    #         pb_account = pbaccount_pb2.Account()
    #         pb_account.ParseFromString(account_cache)
    #     else:
    #         pb_account = await AccountServer().auth_with_token(self.token, app_id=self.app_id_int64, request_id=self.request_id)
    #         if pb_account is None:
    #             raise HTTPError(401, "token expired", reason="token expired")
    #
    #         # set to cache
    #         rd.redis_set(token_key, pb_account.SerializeToString(), 60 * 10)
    #
    #     account = Account(pb_account)
    #     return account

    # @gen.coroutine
    def prepare(self):
    # get post data
        try:
            data = json.loads(self.request.body)
            if data is not None:
                self.post_data = data
        except:
            raise HTTPError(400, "request body parse error",
                            reason="request body parse error")

        # check the server state
        # server_alive, server_status_message = get_server_status("api-gw")
        # if not server_alive:
        #     raise HTTPError(504, server_status_message,
        #                     reason=server_status_message)
    
        if not Config().debug:
            self.app_id = self.post_data.get("app_id", None)
            if not self.app_id:
                raise HTTPError(400, "app id not found", reason="app id not found")
    
            # self.app_id_int64 = int(self.app_id, 36)
            # if not self.app_id_int64:
            #     raise HTTPError(400, "app id invalid", reason="app id invalid")
        
            # # get app version
            # try:
            #     ver = self.get_argument('version', '1.0')
            #     if not ver:
            #         ver = '1.0'
            #     self.app_version = V(ver)
            # except Exception as e:
            #     logging.warning('version argument error:{0}'.format(e))
            #     self.app_version = V('1.0')
        
            # if self.app_version < V(Config().app_version_require.get(self.app_id, '1.0.0')):
            #     raise HTTPError(400, "app version too low",
            #                     reason="app version too low")
        
            # get auth token
            self.token = self.post_data.get('token', None)
        
            # get secret
            self.secret = Config().app_key_secret.get(self.app_id, None)
            if self.secret is None:
                raise HTTPError(400, "app id invalid", reason="app id invalid")
            
        

    def write_error(self, status_code, **kwargs):
        self.set_status(200, reason=self._reason)  # change http code to 200 for restful api
        self.send_to_client_non_encrypt(status_code, self._reason,self._reason)

    def send_to_client(self, error_id=0, message='', response=None):
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        result = dict(error=dict(id=error_id, message=message),
                      response=response)

        self.finish(self._encode(json_encode(result)))

    def send_to_client_non_encrypt(self, status=0, message='', response=None):
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        result = dict(status=status, message=message,response=response)

        self.finish(json.dumps(result,ensure_ascii=False))

    def _encode(self, data):
        secret = Config().app_key_secret.get(self.app_id, None)
        if not secret:
            return data
        secret = hashlib.md5(secret.encode('utf-8')).hexdigest()
        token = secret * \
            int(math.ceil(float(len(data.encode('utf-8'))) / len(secret)))
        xor = bytes([ord(a) ^ b for a, b in zip(token, data.encode('utf-8'))])
        return base64.standard_b64encode(xor)

    def _decode(self, data):
        secret = Config().app_key_secret.get(self.app_id, None)
        if not secret:
            return data
        data = base64.standard_b64decode(data.encode('utf-8'))
        secret = hashlib.md5(secret.encode('utf-8')).hexdigest()
        token = secret * int(math.ceil(float(len(data)) / len(secret)))
        data = bytes([ord(a) ^ b for a, b in zip(token, data)])
        return data.decode('utf-8')


class NotFoundHandler(APIHandler):
    def prepare(self):
        ret = super(NotFoundHandler, self).prepare()
        if ret and ret.exception():
            return ret

        if not self._finished:
            raise HTTPError(404)
