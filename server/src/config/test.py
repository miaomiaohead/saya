# -*- coding:utf-8 -*-

from config import BaseConfig


class TestConfig(BaseConfig):
    """TEST 环境
    """
    ENV = "TEST"

    GITHUB_REDIRECT_URI = "http://localhost:5000/webapi/user/github_login_callback"
