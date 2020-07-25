# -*- coding:utf-8 -*-

import time


class Watcher(object):
    def __init__(self):
        self.create = time.time()
        self.static = False
        self.request_failed = False
        self.cookies = {}

    def delayed(self):
        """输出延时
        """
        now = time.time()
        return int((now - self.create) * 1000)

    def ident(self):
        """请求标识
        """
        return id(self)