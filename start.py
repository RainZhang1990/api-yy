# -*- coding: utf-8 -*
import logging
import os
import signal
import sys

import tornado
from tornado.ioloop import IOLoop
from tornado.options import define, options
from tornado.web import url

import core
# import core.backend
import core.redis
from core.config import Config, Secret
from handler import app,order_batch,spu_classify


def make_app():
    settings = {
        "debug": options.debug,
        "app_name": "API-YY",
        "compress_response": True,
        "template_path" : 'templates', #模板文件目录,想要Tornado能够正确的找到html文件，需要在 Application 中指定文件的位置
        "static_path" : 'static'  #静态文件目录,可用于用于访问js,css,图片之类的添加此配置之后，tornado就能自己找到静态文件
    }

    handlers = [
        url(r"/test", app.TestHandler, name='app.test'),
        url(r"/algorithm/orderbatch", order_batch.GetOrderBatch_LPHandler, name='orderbatch'),
        url(r"/algorithm/spuclassifytest",spu_classify.IndexHandler, name='spuclassifytest'),
        url(r"/algorithm/spuclassify",spu_classify.SPUClassifyHandler, name='spuclassify'),
        url(r"/.*", app.NotFoundHandler, name='error404')
    ]

    return tornado.web.Application(handlers, **settings)


def signal_shutdown_handler(signal, frame):
    del core.backend.backend_user_media

    logging.critical('application exited')
    sys.exit(0)


def main():
    tornado.options.parse_command_line()

    if options.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)

    logging.info('application started')

    # set signal handler
    signal.signal(signal.SIGINT, signal_shutdown_handler)
    signal.signal(signal.SIGTERM, signal_shutdown_handler)

    app = make_app()
    server = tornado.httpserver.HTTPServer(app, xheaders=True)
    server.bind(options.port)
    server.start(4)
    # server.listen(options.port)
    logging.info("{} Server started on port: {}".format(Config().name, options.port))
    IOLoop.current().start()


def init_config():
    #   第一个位置用于实际部署时使用（ 比如 k8s 或 docker 的 volume mapping ）
    #   第二个位置则是默认位置，可用于开发中使用
    filepaths = ['/data/web/config/config.yaml',
                 './config/config.yaml']

    Config().load_config(filepaths)

    # set options
    options.define("debug", default=Config().debug)
    options.define('port', default=Config().port,
                   help='run on the given port', type=int)


def init_secret():
    Secret().load_secret(
        "redis",
        ["host", "port", "password"],
        ["/var/app/secret/", "./secret/"]
    )


if __name__ == '__main__':
    init_config()

    # init_secret()
    #
    # err = core.backend.init_backend()
    # if err:
    #     raise Exception("init backend error: " + err.decode())
    #
    # os.makedirs(Config().uploads_temp_path, exist_ok=True)
    #
    # core.redis.init()

    main()
