# -*- coding:utf-8 -*-


class BaseProto(object):
    @classmethod
    def valid(cls, value):
        ignore_keys = {"__module__", "__doc__"}
        for k, v in cls.__dict__.items():
            if k in ignore_keys:
                continue
            if v == value:
                return True
        return False


class EnumUserCred(BaseProto):
    """身份类型
    """
    ADMIN = "ADMIN"
    USER = "USER"
    GUEST = "GUEST"


class EnumDocStatus(BaseProto):
    """文档状态
    """
    WAIT = "WAIT"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

