# -*- coding:utf-8 -*-

from sanic import Blueprint
from sanic.response import text, json

from webapp import result
from webapp.baselib import req
from webapp.protocol import debug


blue_print = Blueprint("debug", __name__)


@blue_print.route("/", methods=['GET', 'POST'])
async def index(request):
    scopes = list(request.app.router.routes_all.keys())
    scopes.sort()
    return text("\n".join(scopes))


@blue_print.route("/echo", methods=["GET", "POST"])
async def echo(request):
    import os

    sessions = {}
    for k, v in request.ctx.session.items():
        sessions[k] = v

    headers = {}
    for k, v in request.headers.items():
        headers[k] = v

    resp = {
        "url": request.url,
        "method": request.method,
        "content_type": request.content_type,
        "args": request.args,
        "query_args": request.query_args,
        "body": str(request.body),
        "json": request.json,
        "sessions": sessions,
        "headers": headers,
        "cwd": os.getcwd(),
    }
    return json(resp)


@blue_print.route("/health", methods=["GET", "POST"])
async def health(request):
    return result.Result.simple()


@blue_print.route("/test_req", methods=["GET", "POST"])
@req.param(query_proto_class=debug.TestQueryRequest,
           body_proto_class=debug.TestBodyRequest)
async def test_req(request):
    resp = {
        "query": request.ctx.query_proto.__dict__,
        "body": request.ctx.body_proto.__dict__,
    }
    return result.Result.simple(obj=resp)


@blue_print.route("/test_executor", methods=["GET", "POST"])
async def test_executor(request):
    def inner(delay):
        import time
        time.sleep(delay)
        return time.time()

    res = await request.app.executor.submit(inner, 5)
    print(res)
    return result.Result.simple()
