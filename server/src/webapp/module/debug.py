# -*- coding:utf-8 -*-

from sanic import Blueprint, app
from sanic.response import text


blue_print = Blueprint("debug", __name__)


@blue_print.route("/", methods=['GET', 'POST'])
async def debug_index(request):
    scopes = list(request.app.router.routes_all.keys())
    scopes.sort()
    return text("\n".join(scopes))


@blue_print.route("/test_session", methods=['GET', 'POST'])
async def test_session(request):
    if not request.ctx.session.get('foo'):
        request.ctx.session['foo'] = 0

    request.ctx.session['foo'] += 1
    return text(request.ctx.session['foo'])
