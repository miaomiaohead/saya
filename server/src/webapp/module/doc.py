# -*- coding:utf-8 -*-

from sanic import Blueprint

from webapp import result, protocol
from webapp.baselib import receiver
from webapp.service import doc_service


blue_print = Blueprint("doc", __name__)


@blue_print.route("/list")
@receiver.param(query_proto_class=protocol.doc.ListRequest)
async def list_doc(request):
    creator = request.ctx.query_proto.creator
    status = request.ctx.query_proto.status
    start = request.ctx.query_proto.start
    limit = request.ctx.query_proto.limit

    page = await doc_service.list_doc(request, creator, status, start, limit)
    return result.Result.simple(obj=page)
