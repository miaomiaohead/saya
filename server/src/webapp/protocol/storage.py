# -*- coding:utf-8 -*-

from webapp.protocol import base
from webapp.baselib.receiver import Field


class TokenRequest(base.BaseProto):
    path = Field(str, default="")
