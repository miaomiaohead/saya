# -*- coding:utf-8 -*-

from sanic import Blueprint
from sanic.response import redirect

from webapp import result, exception, protocol
from webapp.protocol.user import LoginAsRequest
from webapp.baselib import req, session_helper
from webapp.service import user_service


blue_print = Blueprint("user", __name__)


@blue_print.route("/github_login", methods=['GET', 'POST'])
async def github_login(request):
    params = ["client_id=%s" % "c0073c9a09d97651fc25",
              "redirect_uri=%s" % "http://saya.signalping.com/webapi/user/github_login_callback",
              "login"]
    link_params = "&".join(params)

    login_url = "https://github.com/login/oauth/authorize?%s" % link_params

    return redirect(login_url)


@blue_print.route("/login_as", methods=['GET', 'POST'])
@req.param(query_proto_class=LoginAsRequest)
async def login_as(request):
    uid = request.ctx.query_proto.uid

    user_meta = await user_service.query_user_meta(request, uid)
    if not user_meta:
        raise exception.AppMissingUser()
    session_helper.save_uid(request, user_meta["uid"])
    return result.Result.simple()


@blue_print.route("/", methods=['GET', 'POST'])
@blue_print.route("/profile", methods=['GET', 'POST'])
async def login_as(request):
    user_meta = await user_service.query_user_meta(request, session_helper.get_uid(request))

    if not user_meta:
        user_meta = {
            "uid": session_helper.get_uid(request),
            "cred": protocol.EnumUserCred.GUEST
        }

    return result.Result.simple(obj=user_meta)
