# -*- coding:utf-8 -*-

from flask import Blueprint, redirect, g

from webapp import result, exception, proto
from webapp.share import request_helper, session_helper
from webapp.service import  user_service


blue_print = Blueprint("user", __name__)


@blue_print.route("/github_login", methods=["get", "post"])
def github_login():
    params = ["client_id=%s" % g.watcher.config("GITHUB_CLIENT_ID"),
              "redirect_uri=%s" % g.watcher.config("GITHUB_REDIRECT_URI"),
              "login"]
    link_params = "&".join(params)

    login_url = "https://github.com/login/oauth/authorize?%s" % link_params
    return redirect(login_url)


@blue_print.route("/github_login_callback", methods=["get", "post"])
@request_helper.param(
    request_helper.Argv("code"),
    request_helper.Argv("state", default=None),)
def github_login_callback(code, state):
    github_user = user_service.query_github_user(code, state)
    if not github_user:
        raise exception.AppGitHubRequestError()
    user_meta = user_service.query_user_meta_by_github_id(github_user["id"])
    if not user_meta:
        user_service.insert_user_from_github(github_user)
    else:
        session_helper.save_uid(user_meta["uid"])
    return result.Result.simple()


@blue_print.route("/", methods=["get", "post"])
@blue_print.route("/profile", methods=["get", "post"])
def profile():
    user_meta = user_service.query_user_meta(session_helper.get_uid())
    if not user_meta:
        user_meta = {
            "uid": session_helper.get_uid(),
            "cred": proto.EnumUserCred.GUEST
        }
    return result.Result.simple(obj=user_meta)
