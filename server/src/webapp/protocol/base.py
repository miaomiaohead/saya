# -*- coding:utf-8 -*-


class BaseProto(object):
    def __init__(self):
        pass


class BaseEnum(object):
    @classmethod
    def valid(cls, value):
        ignore_keys = {"__module__", "__doc__"}
        for k, v in cls.__dict__.items():
            if k in ignore_keys:
                continue
            if v == value:
                return True
        return False
