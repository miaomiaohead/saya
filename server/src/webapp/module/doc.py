# -*- coding:utf-8 -*-

from sanic import Blueprint

from webapp import result, protocol, exception
from webapp.baselib import receiver, session_helper
from webapp.service import doc_service, user_service


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


@blue_print.route("/remove", methods=["GET", "POST"])
@receiver.param(query_proto_class=protocol.doc.RemoveRequest,
                body_proto_class=protocol.doc.RemoveRequest)
async def doc_remove(request):
    proto = protocol.merge(request.ctx.query, request.ctx.body_proto)
    doc_id = proto.doc_id

    item = await doc_service.query_doc_meta(request, doc_id)
    if item["creator"] != session_helper.get_uid(request):
        raise exception.AppAccessDeny()

    await doc_service.remove_doc(request, doc_id)
    return result.Result.simple()


@blue_print.route("/post", methods=["GET", "POST"])
@receiver.param(query_proto_class=protocol.doc.PostRequest,
                body_proto_class=protocol.doc.PostRequest)
async def doc_post(request):
    proto = protocol.merge(request.ctx.query, request.ctx.body_proto)
    title = proto.title
    source = proto.source
    desc = proto.desc

    creator = session_helper.get_uid()
    if not await user_service.query_user_meta(request, creator):
        raise exception.AppMissingUser()

    if not source.endswith(".zip"):
        raise exception.AppNotSupportSource()

    doc_id = doc_service.generate_doc_id()
    await doc_service.post_doc(request, doc_id, title, source, desc, creator)
    return result.Result.simple(obj={"doc_id": doc_id})


@blue_print.route("/query")
@receiver.param(query_proto_class=protocol.doc.QueryRequest)
async def query_doc(request):
    doc_id = request.ctx.query_proto.doc_id

    item = await doc_service.query_doc(request, doc_id)
    if not item:
        raise exception.AppMissingDoc()
    return result.Result.simple(obj=item)
