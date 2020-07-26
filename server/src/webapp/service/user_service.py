# -*- coding:utf-8 -*-

import urllib.parse

from sanic.log import logger

from webapp import protocol
from webapp.db import user_db
from webapp.baselib import session_helper


async def query_user_meta(request, uid):
    return await user_db.query_user_meta(uid, pool=request.app.db_pool)


async def query_github_user(request, code, state):
    token = await get_github_token(request, code, state)
    if not token:
        return None

    url = "http://47.92.81.197/user"
    # url = "https://api.github.com/user"
    headers = {
        "Authorization": "token %s" % token,
        "Host": "api.github.com",
    }
    rt = None
    client = None
    try:
        client = request.app.http_clients.get_client("api.github.com")
        r = await client.get(url, headers=headers, ssl=False)
        rt = await r.text()
        return await r.json()
    except Exception as e:
        logger.error("query github user failed, rsp: %s, req headers: %s, e: %s"
                     % (rt, headers, str(e)))
    finally:
        client or (await client.close())


async def get_github_token(request, code, state):
    app = request.app
    payloads = {
        "client_id": app.config.GITHUB_CLIENT_ID,
        "client_secret": app.config.GITHUB_CLIENT_SECRET,
        "redirect_uri": app.config.GITHUB_REDIRECT_URI,
        "code": code,
    }
    if state:
        payloads["state"] = state

    url = "https://github.com/login/oauth/access_token"
    rt = None
    client = None
    try:
        client = request.app.http_clients.get_client("github.com")
        r = await client.post(url, data=payloads, ssl=False)
        rt = await r.text()
        logger.info("get github token resp: %s" % rt)
        resp = urllib.parse.parse_qs(rt)
        return resp["access_token"][0]
    except Exception as e:
        logger.error("get github token failed, rsp: %s, req: %s, e: %s"
                     % (rt, payloads, str(e)))
    finally:
        client or (await client.close())


async def query_user_meta_by_github_id(request, github_id):
    return await user_db.query_user_meta_by_github_id(github_id, pool=request.app.db_pool)


async def insert_user_from_github(request, github_user):
    user = {
        "uid": session_helper.get_uid(request),
        "github_id": github_user["id"],
        "avatar": github_user["avatar_url"],
        "nickname": github_user["login"],
        "cred": protocol.EnumUserCred.USER,
    }
    await user_db.replace_user(user, pool=request.app.db_pool)
