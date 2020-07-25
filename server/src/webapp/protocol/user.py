# -*- coding:utf-8 -*-

from webapp.protocol import base
from webapp.baselib.receiver import Field


class LoginAsRequest(base.BaseProto):
    uid = Field(str)


class GithubLoginCallbackRequest(base.BaseProto):
    code = Field(str)
    state = Field(str, default=None)
