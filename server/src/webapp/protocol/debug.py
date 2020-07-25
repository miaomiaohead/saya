# -*- coding:utf-8 -*-

from webapp import protocol
from webapp.baselib.req import Field


class TestQueryRequest(protocol.BaseProto):
    uid = Field(int)
    name = Field(str, default=None)
    age = Field(int, default=18)


class TestBodyRequest(protocol.BaseProto):
    uid = Field(int)
    name = Field(str, default=None)
    age = Field(int, default=18)

