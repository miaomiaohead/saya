# -*- coding:utf-8 -*-

from flask import session, current_app as app

from webapp.share import helper

__session_keys__ = ("_uid", )


def get_uid():
    return session.get("_uid", None)


def save_uid(uid):
    session["_uid"] = uid


def clear():
    for session_key in __session_keys__:
        session.pop(session_key, None)


def session_sign(urlsafe=False):
    val = app.session_interface.get_signing_serializer(app).dumps(dict(session))
    if urlsafe:
        val = helper.urlsafe_b64encode(val)
    return val
