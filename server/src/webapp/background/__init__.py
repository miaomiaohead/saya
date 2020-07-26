# -*- coding:utf-8 -*-

import asyncio


@asyncio.coroutine
def background_loop(app):
    task_pool = app.background_task_pool

    while True:
        coros = [t.func(app) for t in task_pool.ready_tasks()]
        yield from asyncio.gather(*coros)

        yield from asyncio.sleep(1)

        task_pool.countdown()


@asyncio.coroutine
def init(app):
    app.loop.create_task(background_loop(app))


class BackgroundTask(object):
    def __init__(self, countdown, schedule, task_name, func):
        self.countdown = countdown
        self.schedule = schedule
        self.task_name = task_name
        self.func = func

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)


class BackgroundTaskPool(object):
    def __init__(self):
        self._pool = []

    def add_task(self, schedule, func, init_countdown=None, task_name=None):
        assert schedule > 0

        if init_countdown is None:
            init_countdown = schedule

        back_task = BackgroundTask(countdown=init_countdown,
                                   schedule=schedule,
                                   task_name=task_name,
                                   func=func)
        self._pool.append(back_task)

    def ready_tasks(self):
        return [t for t in self._pool if t.countdown <= 0]

    def countdown(self):
        for t in self._pool:
            t.countdown -= 1
            if t.countdown < 0:
                t.countdown = t.schedule - 1
