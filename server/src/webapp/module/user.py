# -*- coding:utf-8 -*-

from sanic import Blueprint
from sanic.response import redirect

from webapp import result, exception, protocol
from webapp.baselib import receiver, session_helper
from webapp.service import user_service


blue_print = Blueprint("user", __name__)


@blue_print.route("/github_login")
async def github_login(request):
    params = ["client_id=%s" % request.app.config.GITHUB_CLIENT_ID,
              "redirect_uri=%s" % request.app.config.GITHUB_REDIRECT_URI,
              "login"]
    link_params = "&".join(params)

    login_url = "https://github.com/login/oauth/authorize?%s" % link_params

    return redirect(login_url)


@blue_print.route("/login_as", methods=["GET", "POST"])
@receiver.param(query_proto_class=protocol.user.LoginAsRequest,
                body_proto_class=protocol.user.LoginAsRequest)
async def login_as(request):
    proto = protocol.merge(request.ctx.query_proto,
                           request.ctx.body_proto)

    uid = proto.uid

    user_meta = await user_service.query_user_meta(request, uid)
    if not user_meta:
        raise exception.AppMissingUser()
    session_helper.save_uid(request, user_meta["uid"])
    return result.Result.simple()


@blue_print.route("/")
@blue_print.route("/profile")
async def login_as(request):
    user_meta = await user_service.query_user_meta(request, session_helper.get_uid(request))

    if not user_meta:
        user_meta = {
            "uid": session_helper.get_uid(request),
            "cred": protocol.EnumUserCred.GUEST
        }

    return result.Result.simple(obj=user_meta)


@blue_print.route("/github_login_callback")
@receiver.param(query_proto_class=protocol.user.GithubLoginCallbackRequest)
async def github_login_callback(request):
    """
    GitHub OAuth2.0 Authorize Redirect
    """
    code = request.ctx.query_proto.code
    state = request.ctx.query_proto.state

    github_user = await user_service.query_github_user(request, code, state)
    if not github_user:
        raise exception.AppGitHubRequestError()

    user_meta = await user_service.query_user_meta_by_github_id(request, github_user["id"])
    if not user_meta:
        await user_service.insert_user_from_github(request, github_user)
    else:
        session_helper.save_uid(request, user_meta["uid"])

    login_redirect_uri = session_helper.get_login_redirect_uri(request)

    if not login_redirect_uri:
        return redirect("http://saya.signalping.com/webapi/user/profile")

    return redirect(login_redirect_uri)


@blue_print.route("/logout")
async def logout(request):
    """退出登录
    """
    return result.Result.simple()
