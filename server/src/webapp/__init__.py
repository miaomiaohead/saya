# -*- coding:utf-8 -*-

import os
import logging

from concurrent import futures

from sanic import Sanic, log
from sanic.log import logger

from webapp import background, hook
from webapp.module import debug, user, storage, doc
from webapp.baselib import session, thread_executor
from webapp.background import debug_back

from tools import kodo, statistic_helper


def create_time_rotating_log_handler(logger_file,
                                     logger_level,
                                     logger_when,
                                     logger_interval,
                                     logger_backup_count,
                                     logger_format, ):
    if not os.path.exists(os.path.dirname(logger_file)):
        os.mkdir(os.path.dirname(logger_file))
    log_handler_init = logging.handlers.TimedRotatingFileHandler
    log_handler = log_handler_init(logger_file,
                                   when=logger_when,
                                   interval=logger_interval,
                                   encoding='UTF-8',
                                   backupCount=logger_backup_count)
    log_handler.setLevel(logger_level)
    log_handler.setFormatter(logging.Formatter(logger_format))
    return log_handler


def create_app(config):
    # init log config
    log_config = log.LOGGING_CONFIG_DEFAULTS
    log_config["formatters"]["generic"]["format"] = config.LOGGER_FORMAT

    # create app
    app = Sanic(__name__, log_config=log_config)
    app.config.from_object(config)

    # init log
    error_log_file = config.LOGGER_FILE + ".ERROR"
    logger.setLevel(config.LOGGER_LEVEL)
    log_handler = create_time_rotating_log_handler(config.LOGGER_FILE,
                                                   config.LOGGER_LEVEL,
                                                   config.LOGGER_WHEN,
                                                   config.LOGGER_INTERVAL,
                                                   config.LOGGER_BACKUP_COUNT,
                                                   config.LOGGER_FORMAT, )
    error_log_handler = create_time_rotating_log_handler(error_log_file,
                                                         logging.ERROR,
                                                         config.LOGGER_WHEN,
                                                         config.LOGGER_INTERVAL,
                                                         config.LOGGER_BACKUP_COUNT,
                                                         config.LOGGER_FORMAT, )
    logger.addHandler(log_handler)
    logger.addHandler(error_log_handler)

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
    app.blueprint(storage.blue_print, url_prefix='/webapi/storage')
    app.blueprint(doc.blue_print, url_prefix='/webapi/doc')

    # register hook
    hook.register(app)

    # register background
    app.background_task_pool = background.BackgroundTaskPool()
    app.background_task_pool.add_task(1, debug_back.handle_per_second)
    app.background_task_pool.add_task(2, debug_back.handle_two_second)

    app.add_task(background.init)

    return app
