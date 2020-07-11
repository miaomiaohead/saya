# -*- coding:utf-8 -*-

import functools

from flask import g

from webapp import exception
from webapp.share import session_helper
from webapp.service import user_service


def authn(*roles):
    """登录态认证
    """
    if not roles:
        g.watcher.error("roles is empty")
        raise exception.AppException()
    roles_set = set(roles)

    def inner_wrapper(f):
        @functools.wraps(f)
        def inner(*ks, **kws):
            uid = session_helper.get_uid()
            if not uid:
                g.watcher.error("session missing uid: %s" % uid)
                raise exception.AppAccessDeny()
            if roles_set and not user_service.user_in_roles(uid, roles_set):
                g.watcher.error("deny access, role invalid, uid: %s" % uid)
                raise exception.AppAccessDeny()
            rv = f(*ks, **kws)
            return rv

        return inner

    return inner_wrapper
