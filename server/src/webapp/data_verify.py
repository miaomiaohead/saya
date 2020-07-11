# -*- coding:utf-8 -*-

from webapp import proto
from webapp.service import vercode_service


def verify_string(key, value, conditions, data):
    ok = isinstance(value, str)
    if not ok:
        return "%s 不是字符串" % key


def verify_number(key, value, conditions, data):
    ok = isinstance(value, int) or isinstance(value, float)
    if not ok:
        return "%s 不是数值" % key


def verify_boolean(key, value, conditions, data):
    ok = isinstance(value, bool)
    if not ok:
        return "%s 不是布尔值" % key


def verify_vercode(key, value, conditions, data):
    if not conditions or not isinstance(conditions, list):
        return False
    key = data.get(conditions[0])
    vercode = vercode_service.query_verify_code(key, proto.EnumVercodeBusiness.REGISTER)
    ok = vercode == value
    if not ok:
        return "验证码错误"


def verify_equal(key, value, conditions, data):
    for condition in conditions:
        if value != data.get(condition):
            return "%s 和 %s 不匹配" % (key, condition)


handlers = {
    "str": verify_string,
    "string": verify_string,
    "number": verify_number,
    "bool": verify_boolean,
    "boolean": verify_boolean,
    "verify_code": verify_vercode,
    "equal": verify_equal,
}
