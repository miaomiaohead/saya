# -*- coding:utf-8 -*-

from sanic import Blueprint

from webapp import result, exception, protocol
from webapp.baselib import receiver, session_helper
from webapp.service import user_service


blue_print = Blueprint("storage", __name__)


@blue_print.route("/token")
@receiver.param(query_proto_class=protocol.storage.TokenRequest)
async def token(request):
    path = request.ctx.query_proto.path

    uid = session_helper.get_uid(request)
    if not await user_service.query_user_meta(request, uid):
        raise exception.AppMissingUser()

    actual_path = f"user/{uid}/{path}"
    upload_token = request.app.kodo_client.upload_token(actual_path)
    resp = {
        "token": upload_token,
        "path": actual_path,
    }

    return result.Result.simple(obj=resp)
