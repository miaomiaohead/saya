# -*- coding:utf-8 -*-

import os
import logging


class BaseConfig(object):
    """测试环境配置
    """
    DEBUG = False
    PORT = 5005
    DES_KEY = "ABCDEFGH"
    ENV = "formal"
    STATISTIC_FILE = "../statistics/statistic.log"

    # SESSION配置
    SECRET_KEY = "123456"
    # SESSION_COOKIE_DOMAIN = "www.cjtx.com.cn"

    # 日志配置
    LOGGER_LEVEL = logging.INFO
    LOGGER_FORMAT = "[%(levelname)s] [%(asctime)s]%(message)s"
    LOGGER_FILE = "../logs/saya.log"
    LOGGER_WHEN = "D"
    LOGGER_INTERVAL = 1
    LOGGER_BACKUP_COUNT = 7
    LOGGER_SUFFIX = "%Y-%m-%d_%H:%M:%S.log"

    # MySQL配置
    DATABASE_NAME = "saya_db"
    DATABASE_HOST = "saya.signalping.com"
    DATABASE_PORT = 3309
    DATABASE_USER = "root"
    DATABASE_PASSWORD = "root@saya"

    # 七牛云
    QINIU_PUBLIC_STORE_REGION = 'https://upload-z1.qiniup.com'
    QINIU_ACCESS_KEY = 'sRd2-QgwgZnPgZyY1E6oS0QxtFWjGLNJwss9D2Op'
    QINIU_SECRET_KEY = 'r4ZiD533tHlAzL9icthxkzjo1OD9PavzFQTLT7an'
    QINIU_PUBLIC_BUCKET = 'saya'

    # GitHub 登录配置
    GITHUB_CLIENT_ID = "c0073c9a09d97651fc25"
    GITHUB_CLIENT_SECRET = "c9fae2e6624e6bde6d4e1e215f406e2da2a840fd"
    GITHUB_REDIRECT_URI = "http://saya.signalping.com/webapi/user/github_login_callback"


class LocalConfig(BaseConfig):
    PORT = 5000
    GITHUB_REDIRECT_URI = "http://localhost:5000/webapi/user/github_login_callback"


class FormalConfig(BaseConfig):
    pass


local = LocalConfig()
formal = FormalConfig()
env_config = {
    "local": local,
    "formal": formal,
}
