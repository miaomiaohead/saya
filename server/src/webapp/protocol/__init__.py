# -*- coding:utf-8 -*-

import copy

from webapp.protocol import base, debug, storage, user


def merge(lft, rgt):
    if lft and not rgt:
        return copy.deepcopy(lft)

    if rgt and not lft:
        return copy.deepcopy(rgt)

    if type(lft) is not type(rgt):
        raise TypeError("left(%s) is not right(%s)" % (type(lft), type(rgt)))

    target_proto = copy.deepcopy(lft)
    for k, v in rgt.__dict__.items():
        if isinstance(v, base.BaseProto):
            res = merge(target_proto.get(k), v)
        else:
            res = v
        target_proto.__dict__[k] = res

    return target_proto


class EnumUserCred(base.BaseEnum):
    """身份类型
    """
    ADMIN = "ADMIN"
    USER = "USER"
    GUEST = "GUEST"


class EnumDocStatus(base.BaseEnum):
    """文档状态
    """
    WAIT = "WAIT"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


