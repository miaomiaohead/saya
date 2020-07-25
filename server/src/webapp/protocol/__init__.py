# -*- coding:utf-8 -*-

# from webapp.protocol import debug


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


class EnumUserCred(BaseEnum):
    """身份类型
    """
    ADMIN = "ADMIN"
    USER = "USER"
    GUEST = "GUEST"


class EnumDocStatus(BaseEnum):
    """文档状态
    """
    WAIT = "WAIT"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
