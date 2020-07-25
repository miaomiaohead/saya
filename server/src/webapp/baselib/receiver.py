# -*- coding:utf-8 -*-

import functools

from sanic.log import logger

from webapp import exception


PLACEHOLDER = object()
MAX_DEEP = 32


class Field(object):
    def __init__(self, type_, default=PLACEHOLDER, name=None):
        self.type_ = type_
        self.default = default
        self.name = name


class Obj(object):
    def __init__(self, type_, default=PLACEHOLDER, name=None):
        self.type_ = type_
        self.default = default
        self.name = name


def dict_to_proto(proto_class, dic, deep=0):
    assert deep < MAX_DEEP

    proto = proto_class()

    for name, field in proto_class.__dict__.items():
        try:
            if isinstance(field, Field):
                val = dic[name]
                try:
                    proto.__dict__[name] = field.type_(val)
                except ValueError:
                    logger.error("'%s' (%s) parse error, expect: %s" % (name, val, field.type_))
                    raise exception.AppInvalidRequest() from None

            if isinstance(field, Obj):
                proto.__dict__[name] = dict_to_proto(field.type_, dic[name], deep+1)
        except KeyError:
            if field.default != PLACEHOLDER:
                proto.__dict__[name] = field.default
            else:
                logger.error("'%s' is None" % name)
                raise exception.AppInvalidRequest() from None

    return proto


def parse_proto(request, query_proto_class, body_proto_class):
    content_type = request.content_type

    query_proto, body_proto = None, None

    if query_proto_class:
        # {"k1":["v1"], "k2": ["v2", "v3"]} ---> {"k1":"v1", "k2": ["v2", "v3"]}
        args = dict((k, v[0] if len(v) == 1 else v) for k, v in request.args.items())
        query_proto = dict_to_proto(query_proto_class, args)

    if body_proto_class and "application/json" in content_type and request.json:
        body_proto = dict_to_proto(body_proto_class, request.json)

    if body_proto_class and content_type == "application/x-www-form-urlencoded" and request.form:
        # {"k1":["v1"], "k2": ["v2", "v3"]} ---> {"k1":"v1", "k2": ["v2", "v3"]}
        form = dict((k, v[0] if len(v) == 1 else v) for k, v in request.form.items())
        body_proto = dict_to_proto(body_proto_class, form)

    return query_proto, body_proto


def param(query_proto_class=None, body_proto_class=None):
    def wrapper(f):
        @functools.wraps(f)
        async def inner(request, *ks, **kws):
            query_proto, body_proto = parse_proto(request, query_proto_class, body_proto_class)

            request.ctx.query_proto = query_proto
            request.ctx.body_proto = body_proto

            ret = await f(request, *ks, **kws)
            return ret
        return inner
    return wrapper
