# -*- coding:utf-8 -*-

from flask import session, current_app as app

from webapp.share import helper

__session_keys__ = ("_uid", "_login_redirect_uri")


def get_uid():
    return session.get("_uid", None)


def save_uid(uid):
    session["_uid"] = uid


def get_login_redirect_uri():
    return session.get("_login_redirect_uri", None)


def save_login_redirect_uri(redirect_uri):
    session["_login_redirect_uri"] = redirect_uri


def remove_login_redirect_uri():
    session["_login_redirect_uri"] = None


def clear():
    for session_key in __session_keys__:
        session.pop(session_key, None)


def session_sign(urlsafe=False):
    val = app.session_interface.get_signing_serializer(app).dumps(dict(session))
    if urlsafe:
        val = helper.urlsafe_b64encode(val)
    return val
