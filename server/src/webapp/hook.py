# -*- coding:utf-8 -*-

from flask import request, g, session
from webapp import exception, result
from webapp.share import helper, session_helper
from webapp.service import user_service

__bad_request_status__ = 400
__ok_request_status__ = 200


def register(app):
    @app.before_request
    def before_request():
        """记录请求信息
        """
        # 请求对象g绑定Watcher
        g.watcher = helper.Watcher()
        # 请求中的包含Token时, 用Token作为session
        # 打印信息
        g.watcher.info("url : %s, methods : %s, request body : %s"
                       % (request.url, request.method, request.get_data()))
        if not session_helper.get_uid():
            session_helper.save_uid(user_service.generate_uid())
        g.current_user = None

    @app.after_request
    def after_request(rv):
        try:
            return rv
        finally:
            data = rv.get_data() if rv.is_sequence else "<static file response>"
            message = "url : %s, method : %s, cost: %s ms, status: %s, response body: %s" \
                      % (request.url, request.method, g.watcher.delayed(), rv.status, data)
            watcher_log_print = g.watcher.info
            # if "404" not in rv.status:
            if "200" not in rv.status or g.watcher.request_failed:
                watcher_log_print = g.watcher.error
                g.watcher.request_failed = True
            if "404" not in rv.status:
                watcher_log_print(message)
                if not g.watcher.request_failed:
                    app.statistic_helper.append_record(subject="REQUEST_SUCCESS", key=request.path, value=1)
                app.statistic_helper.append_record(subject="REQUEST_TOTAL", key=request.path, value=1)
                app.statistic_helper.append_record(subject="REQUEST_DELAY", key=request.path, value=g.watcher.delayed())

    @app.errorhandler(exception.AppException)
    def exception_handler(e):
        message = str(e)
        status = __ok_request_status__
        error_result = result.Result.error(e.error_code(), message)
        g.watcher.request_failed = True
        g.watcher.error("url : %s, methods : %s, request body : %s, cost: %s ms "
                        % (request.url, request.method, request.get_data(), g.watcher.delayed()))
        app.statistic_helper.append_record(subject="REQUEST_FAILED", key=request.path, value=1)
        return error_result, status
