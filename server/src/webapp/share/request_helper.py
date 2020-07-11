# -*- coding:utf-8 -*-

import functools
from flask import request, g
from webapp import exception

# TODO(lu) 支持JSON解析
__empty_object__ = object()


def _get_val(struct_, k, t):
    if t == list or t == tuple or t == set:
        return struct_.getlist(k)
    return struct_.get(k)


class Argv(object):
    def __init__(self, name, *, type_=str, default=__empty_object__, maximum=None, minimum=None):
        self.__arg_name__ = name
        self.__type__ = type_
        self.__default__ = default
        self.__maximum__ = maximum
        self.__minimum__ = minimum

    def name(self):
        return self.__arg_name__

    def val(self, only_get):
        name = self.__arg_name__
        value = None
        method = request.method
        content_type = request.content_type
        if method == "GET" or only_get:
            value = _get_val(request.args, name, self.__type__)
        elif method == "POST" and content_type == 'application/x-www-form-urlencoded':
            value = _get_val(request.form, name, self.__type__)
        elif method == "POST" and 'application/json' in content_type:
            value = request.json.get(name, None)
        # value为空，并且默认值为empty_object, 则认为没有默认值 抛出异常
        if value is None and self.__default__ is __empty_object__:
            g.watcher.error("'%s' is None" % name)
            raise exception.AppInvalidRequest()

        # value为空 取默认值, 默认值仍然为空，直接返回None
        if value is None:
            value = self.__default__
        if value is None:
            return None

        # 解析参数类型
        try:
            value = self.__type__(value)
        except Exception as e:
            g.watcher.error("'%s' parse error, except : %s" % (name, e))
            raise exception.AppInvalidRequest()

        # 判断最大最小值
        if self.__maximum__ and value > self.__maximum__:
            g.watcher.error("'%s' invalid, maximum: %s, value: %s"
                            % (name, self.__maximum__, value))
            raise exception.AppInvalidRequest()
        if self.__minimum__ and value < self.__minimum__:
            g.watcher.error("'%s' invalid, minimum: %s, value: %s"
                            % (name, self.__maximum__, value))
            raise exception.AppInvalidRequest()
        return value


def param(*args, only_get=False):
    if not isinstance(args, tuple):
        raise Exception("parameters is not list")

    def wrapper(f):
        @functools.wraps(f)
        def inner(*ks, **kws):
            for arg in args:
                name = arg.name()
                value = arg.val(only_get)
                kws[name] = value
            rv = f(*ks, **kws)
            return rv

        return inner

    return wrapper
