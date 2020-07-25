# -*- coding:utf-8 -*-

import asyncio


class ThreadExecutor(object):
    def __init__(self, pool):
        self._pool = pool

    def submit(self, fn, *args, **kwargs):
        ft = self._pool.submit(fn, *args, **kwargs)
        return asyncio.wrap_future(ft)
