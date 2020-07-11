# -*- coding:utf-8 -*-

import os
import logging
import logging.handlers

from flask import Flask

from webapp import hook, db
from webapp.share import encrypt_helper, kodo, statistic_helper
from webapp.module import debug, user, doc, storage


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


def create_app(configure):
    # 创建服务器
    app = Flask(__name__)

    # 导入配置对象
    app.config.from_object(configure)

    # ENV导入环境变量
    os.environ["SERVER_ENV"] = configure.ENV

    # des加密解密工具
    app.des_helper = encrypt_helper.DesHelper(configure.DES_KEY)

    # 数据库连接
    if configure.DATABASE_NAME is not None:
        db_connect_pool = db.create_connect_pool(configure.DATABASE_HOST,
                                                 configure.DATABASE_USER,
                                                 configure.DATABASE_PASSWORD,
                                                 configure.DATABASE_NAME,
                                                 configure.DATABASE_PORT)
        app.db_connect_pool = db_connect_pool

    # 日志系统
    error_log_file = configure.LOGGER_FILE + ".ERROR"
    app.logger.setLevel(configure.LOGGER_LEVEL)
    log_handler = create_time_rotating_log_handler(configure.LOGGER_FILE,
                                                   configure.LOGGER_LEVEL,
                                                   configure.LOGGER_WHEN,
                                                   configure.LOGGER_INTERVAL,
                                                   configure.LOGGER_BACKUP_COUNT,
                                                   configure.LOGGER_FORMAT, )
    error_log_handler = create_time_rotating_log_handler(error_log_file,
                                                         logging.ERROR,
                                                         configure.LOGGER_WHEN,
                                                         configure.LOGGER_INTERVAL,
                                                         configure.LOGGER_BACKUP_COUNT,
                                                         configure.LOGGER_FORMAT, )
    app.logger.addHandler(log_handler)
    app.logger.addHandler(error_log_handler)

    # 统计工具初始化
    app.statistic_helper = statistic_helper.StatisticHelper(configure.STATISTIC_FILE)

    # 七牛云对象存储
    app.kodo_client = kodo.KodoClient(configure.QINIU_PUBLIC_STORE_REGION,
                                      configure.QINIU_ACCESS_KEY,
                                      configure.QINIU_SECRET_KEY,
                                      configure.QINIU_PUBLIC_BUCKET)

    # 注册蓝图
    app.register_blueprint(debug.blue_print, url_prefix='/webapi/debug')
    app.register_blueprint(user.blue_print, url_prefix='/webapi/user')
    app.register_blueprint(doc.blue_print, url_prefix='/webapi/doc')
    app.register_blueprint(storage.blue_print, url_prefix='/webapi/storage')

    # 注册请求hook
    hook.register(app)

    return app
