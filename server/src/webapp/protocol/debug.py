# -*- coding:utf-8 -*-

from webapp.protocol import base
from webapp.baselib.receiver import Field


class TestReqRequest(base.BaseProto):
    uid = Field(int)
    name = Field(str, default=None)
    age = Field(int, default=18)

