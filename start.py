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
import ir_fit
from core import redis,oss,config
from core.config import Config
from handler import app,order_batch,image_retrieval,relevance


def make_app():
    settings = {
        "debug": options.debug,
        "app_name": Config().name,
        "compress_response": True,
        "template_path" : 'templates', #模板文件目录,想要Tornado能够正确的找到html文件，需要在 Application 中指定文件的位置
        "static_path" : 'static'  #静态文件目录,可用于用于访问js,css,图片之类的添加此配置之后，tornado就能自己找到静态文件
    }

    handlers = [
        url(r"/test", app.TestHandler, name='app.test'),
        url(r"/algorithm/warehouse/orderbatchan", order_batch.OrderBatchAnHandler, name='OrderBatchAn'),
        url(r"/algorithm/warehouse/orderbatchsn", order_batch.OrderBatchSnHandler, name='OrderBatchSn'),
        url(r"/algorithm/order/relevance", relevance.RelevanceHandler, name='Relevance'),
        url(r"/algorithm/imageretrieval/test",image_retrieval.IndexHandler, name='IrTest'),
        url(r"/algorithm/imageretrieval/imageretrieval",image_retrieval.ImageRetrivalHandler, name='ImageRetrieval'),
        url(r"/algorithm/imageretrieval/fit",image_retrieval.IrFitHandler, name='IrFit'),
        url(r"/algorithm/imageretrieval/label",image_retrieval.IrLabelHandler, name='IrLabel'),
        url(r"/algorithm/imageretrieval/fitstatus",image_retrieval.IrFitStatusHandler, name='IrFitStatus'),
        url(r"/.*", app.NotFoundHandler, name='error404')
    ]

    return tornado.web.Application(handlers, **settings)


def signal_shutdown_handler(signal, frame):
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
    server = tornado.httpserver.HTTPServer(app, xheaders=True,max_buffer_size=1048576000) # 最大文件上传尺寸1000M
    server.bind(options.port)
    server.start(options.thread)
    # server.listen(options.port)
    logging.info("{} Server started on port: {}".format(Config().name, options.port))
    IOLoop.current().start()


def init_options():
    # set options
    options.define("debug", default=Config().debug)
    options.define("thread", default=Config().thread)
    options.define('port', default=Config().port,
                   help='run on the given port', type=int)


if __name__ == '__main__':
    config.init()
    redis.init()
    redis.listen()
    oss.init()
    init_options()
    ir_fit.main(Config().image_retrieval.get('fit_workers'))
    main()
 