# -*- coding:utf-8 -*-

import time
import uuid

from sanic.log import logger

from webapp import db, exception, result
from webapp.baselib import session, watcher, http_clients


def load_session_from_request(request):
    local_session = session.Session(request.app.session_config)
    try:
        local_session.load_request_cookie(request)
    except Exception:
        pass
    finally:
        request.ctx.session = local_session


def register(app):

    @app.listener('before_server_start')
    async def setup_component(local_app, loop):
        # 初始化 db
        app.db_pool = await db.create_db_pool(local_app, loop)

        # register http client
        app.http_clients = http_clients.HttpClients(loop)
        app.http_clients.add_client("github.com")
        app.http_clients.add_client("api.github.com")

    @app.middleware('request')
    async def before_request(request):
        request.ctx.start_time = time.time()
        request.ctx.watcher = watcher.Watcher()

        load_session_from_request(request)

        if not request.ctx.session.get("_uid"):
            request.ctx.session["_uid"] = str(uuid.uuid4())

        logger.info("url : %s, methods : %s, request body : %s"
                    % (request.url, request.method, str(request.body)))

    @app.middleware('response')
    async def after_request(request, response):
        try:
            local_session = request.ctx.session
            local_session.inject_response_cookie(response)
        except AttributeError:
            pass
        finally:
            delayed = request.ctx.watcher.delayed()
            request_failed = request.ctx.watcher.request_failed

            message = "url : %s, method : %s, cost: %s ms, status: %s, response body: %s" \
                      % (request.url, request.method, delayed, response.status, str(response.body))

            logger_print = logger.info
            if response.status != 200 or request_failed:
                logger_print = logger.error

            if response.status != 404:
                logger_print(message)
                if not request_failed:
                    app.statistic_helper.append_record(subject="REQUEST_SUCCESS", key=request.path, value=1)
                app.statistic_helper.append_record(subject="REQUEST_TOTAL", key=request.path, value=1)
                app.statistic_helper.append_record(subject="REQUEST_DELAY", key=request.path, value=delayed)

    @app.exception(exception.AppException)
    async def filter_exception(request, e):
        request.ctx.watcher.request_failed = True
        app.statistic_helper.append_record(subject="REQUEST_FAILED", key=request.path, value=1)
        resp = {
            "error_code": e.error_code(),
            "error_message": str(e),
        }
        return result.Result.obj(resp)
