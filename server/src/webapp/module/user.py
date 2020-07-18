# -*- coding:utf-8 -*-

from flask import Blueprint, redirect, g

from webapp import result, exception, proto
from webapp.share import request_helper, session_helper
from webapp.service import user_service


blue_print = Blueprint("user", __name__)


@blue_print.route("/login_as", methods=["get", "post"])
@request_helper.param(
    request_helper.Argv("uid"),)
def login_as(uid):
    user_meta = user_service.query_user_meta(uid)
    if not user_meta:
        raise exception.AppMissingUser()
    session_helper.save_uid(user_meta["uid"])
    return result.Result.simple()


@blue_print.route("/github_login", methods=["get", "post"])
@request_helper.param(
    request_helper.Argv("redirect_uri", default=None),)
def github_login(redirect_uri):
    """使用 GitHub OAuth2.0 登录

    :param str redirect_uri: 登录完成后的重定向地址
    """
    params = ["client_id=%s" % g.watcher.config("GITHUB_CLIENT_ID"),
              "redirect_uri=%s" % g.watcher.config("GITHUB_REDIRECT_URI"),
              "login"]
    link_params = "&".join(params)

    session_helper.save_login_redirect_uri(redirect_uri)

    login_url = "https://github.com/login/oauth/authorize?%s" % link_params
    return redirect(login_url)


@blue_print.route("/github_login_callback", methods=["get", "post"])
@request_helper.param(
    request_helper.Argv("code"),
    request_helper.Argv("state", default=None),)
def github_login_callback(code, state):
    """
    GitHub OAuth2.0 Authorize Redirect

    :param code: GitHub OAuth2.0 Authorize Code
    :param state: GitHub OAuth2.0 state
    """
    github_user = user_service.query_github_user(code, state)
    if not github_user:
        raise exception.AppGitHubRequestError()
    user_meta = user_service.query_user_meta_by_github_id(github_user["id"])
    if not user_meta:
        user_service.insert_user_from_github(github_user)
    else:
        session_helper.save_uid(user_meta["uid"])

    login_redirect_uri = session_helper.get_login_redirect_uri()

    if not login_redirect_uri:
        return redirect("http://saya.signalping.com/webapi/user/profile")

    return redirect(login_redirect_uri)


@blue_print.route("/", methods=["get", "post"])
@blue_print.route("/profile", methods=["get", "post"])
def profile():
    """查询用户信息
    """
    user_meta = user_service.query_user_meta(session_helper.get_uid())
    if not user_meta:
        user_meta = {
            "uid": session_helper.get_uid(),
            "cred": proto.EnumUserCred.GUEST
        }
    return result.Result.simple(obj=user_meta)


@blue_print.route("/logout", methods=["get", "post"])
def logout():
    """退出登录
    """
    session_helper.clear()
    return result.Result.simple()
