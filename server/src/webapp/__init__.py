# -*- coding:utf-8 -*-

from concurrent import futures

from sanic import Sanic

from webapp import background, hook
from webapp.module import debug, user
from webapp.baselib import session, thread_executor

from tools import kodo, statistic_helper


def create_app(config):
    app = Sanic(__name__)
    app.config.from_object(config)

    # init session config
    app.session_config = session.SessionConfig(app.config.SECRET_KEY)

    # init kodo
    app.kodo_client = kodo.KodoClient(app.config.QINIU_PUBLIC_STORE_REGION,
                                      app.config.QINIU_ACCESS_KEY,
                                      app.config.QINIU_SECRET_KEY,
                                      app.config.QINIU_PUBLIC_BUCKET)

    # 初始化 线程池 worker
    max_workers = app.config.EXECUTOR_MAX_WORKERS
    app.executor = thread_executor.ThreadExecutor(futures.ThreadPoolExecutor(max_workers=max_workers))

    # 统计工具初始化
    app.statistic_helper = statistic_helper.StatisticHelper(app.config.STATISTIC_FILE)

    # register route
    app.blueprint(debug.blue_print, url_prefix='/webapi/debug')
    app.blueprint(user.blue_print, url_prefix='/webapi/user')

    # register hook
    hook.register(app)

    # register background
    app.add_task(background.init)

    return app
