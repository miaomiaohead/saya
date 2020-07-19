# -*- coding:utf-8 -*-

from sanic import Sanic

from sanic_session import Session

from webapp import background, hook
from webapp.module import debug


def create_app():
    app = Sanic(__name__)
    Session(app)

    # register route
    app.blueprint(debug.blue_print, url_prefix='/webapi/debug')

    # register hook
    hook.register(app)

    # register background
    app.add_task(background.init)

    return app
