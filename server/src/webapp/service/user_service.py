# -*- coding:utf-8 -*-

import uuid
import requests
import urllib.parse

from flask import g

from webapp import proto, exception
from webapp.db import user_db
from webapp.share import session_helper


def generate_uid():
    return str(uuid.uuid4())


def query_github_user(code, state):
    token = get_github_token(code, state)
    if not token:
        return None

    url = "https://api.github.com/user"
    headers = {
        "Authorization": "token %s" % token,
    }
    r = None
    try:
        r = requests.get(url, headers=headers)
        return r.json()
    except Exception as e:
        g.watcher.error("query github user failed, rsp: %s, req headers: %s, e: %s"
                        % (r and r.text, headers, str(e)))


def get_github_token(code, state):
    payloads = {
        "client_id": g.watcher.config("GITHUB_CLIENT_ID"),
        "client_secret": g.watcher.config("GITHUB_CLIENT_SECRET"),
        "redirect_uri": g.watcher.config("GITHUB_REDIRECT_URI"),
        "code": code,
    }
    if not state:
        payloads["state"] = state

    url = "https://github.com/login/oauth/access_token"
    r = None
    try:
        r = requests.post(url, data=payloads, timeout=60)
        g.watcher.info("get github token resp: %s" % r.text)
        resp = urllib.parse.parse_qs(r.text)
        return resp["access_token"][0]
    except Exception as e:
        g.watcher.error("get github token failed, rsp: %s, req: %s, e: %s"
                        % (r and r.text, payloads, str(e)))


def query_user_meta_by_github_id(github_id):
    user_db.query_user_meta_by_github_id(github_id)


def insert_user_from_github(github_user):
    user = {
        "uid": session_helper.get_uid(),
        "github_id": github_user["id"],
        "avatar": github_user["avatar_url"],
        "nickname": github_user["login"],
        "cred": proto.EnumUserCred.USER,
    }
    user_db.replace_user(user)


def query_user_meta(uid):
    return user_db.query_user_meta(uid)
