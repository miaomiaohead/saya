# -*- coding:utf-8 -*-

from webapp.protocol import base
from webapp.baselib.receiver import Field


class ListRequest(base.BaseProto):
    creator = Field(int, default=None)
    status = Field(str, default=None)
    start = Field(int, default=0)
    limit = Field(int, default=20)


class RemoveRequest(base.BaseProto):
    doc_id = Field(str)


class PostRequest(base.BaseProto):
    title = Field(str)
    source = Field(str)
    desc = Field(str, default="")


class QueryRequest(base.BaseProto):
    doc_id = Field(str)
