# -*- coding:utf-8 -*-

from flask import Blueprint, current_app as app

from webapp import result, exception
from webapp.share import request_helper, session_helper
from webapp.service import user_service


blue_print = Blueprint("storage", __name__)


@blue_print.route("/token", methods=["get", "post"])
@request_helper.param(
    request_helper.Argv("path", default=""))
def token(path):
    uid = session_helper.get_uid()
    if not user_service.query_user_meta(uid):
        raise exception.AppMissingUser()

    actual_path = f"user/{uid}/{path}"
    upload_token = app.kodo_client.upload_token(actual_path)
    resp = {
        "token": upload_token,
        "path": actual_path,
    }
    return result.Result.simple(obj=resp)

