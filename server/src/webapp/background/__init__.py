# -*- coding:utf-8 -*-

import asyncio


@asyncio.coroutine
def handle_per_second(app):
    pass


@asyncio.coroutine
def background_loop(app):
    while True:
        yield from asyncio.sleep(1)
        yield from asyncio.gather(handle_per_second(app),)


@asyncio.coroutine
def init(app):
    app.loop.create_task(background_loop(app))
