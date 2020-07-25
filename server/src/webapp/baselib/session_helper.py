
# -*- coding:utf-8 -*-


__session_keys__ = ("_uid", "_login_redirect_uri")


def get_uid(request):
    return request.ctx.session.get("_uid", None)


def save_uid(request, uid):
    request.ctx.session.set("_uid", uid)


def get_login_redirect_uri(request):
    return request.ctx.session.get("_login_redirect_uri", None)


def save_login_redirect_uri(request, redirect_uri):
    request.ctx.session.set("_login_redirect_uri", redirect_uri)


def remove_login_redirect_uri(request):
    request.ctx.session.set("_login_redirect_uri", None)


# def clear(request):
#     for session_key in __session_keys__:
#         request.ctx.session.pop(session_key, None)
