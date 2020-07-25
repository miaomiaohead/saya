# -*- coding:utf-8 -*-

from webapp import protocol
from webapp.baselib.req import Field


class LoginAsRequest(protocol.BaseProto):
    uid = Field(str)


class GithubLoginCallbackRequest(protocol.BaseProto):
    code = Field(str)
    state = Field(str, default=None)
