# -*- coding:utf-8 -*-

from flask import Blueprint, g

from webapp import result, exception
from webapp.share import request_helper, session_helper
from webapp.service import doc_service, user_service


blue_print = Blueprint("doc", __name__)


@blue_print.route("/list", methods=["get", "post"])
@request_helper.param(
    request_helper.Argv("creator", default=None),
    request_helper.Argv("status", default=None),
    request_helper.Argv("start", type_=int, default=0),
    request_helper.Argv("limit", type_=int, default=20),)
def doc_list(creator, status, start, limit):
    """列出文档

    .. code-block::

        (GET) http://saya.signalping.com/webapi/doc/list

    :param creator: 列出指定用户创建的文档，未填时列出所有用户文档。
    :type creator: str or None
    :param status: 列出指定状态的文档，未填时列出所有状态文档。
    :type status: str or None
    :param int start: 数据获取偏移，默认为0。
    :param int limit: 数据获取的最大个数，默认为20。
    :return: :class:`Page <webapp.data_model.Page>` (:class:`Document <webapp.data_model.Document>`)，。
    """
    page = doc_service.list_doc(creator, status, start, limit)
    return result.Result.simple(obj=page)


@blue_print.route("/remove", methods=["get", "post"])
@request_helper.param(
    request_helper.Argv("doc_id"),)
def doc_remove(doc_id):
    item = doc_service.query_doc_meta(doc_id)
    if item["creator"] != session_helper.get_uid():
        raise exception.AppAccessDeny()

    doc_service.remove_doc(doc_id)
    return result.Result.simple()


@blue_print.route("/post", methods=["get", "post"])
@request_helper.param(
    request_helper.Argv("title"),
    request_helper.Argv("source"),
    request_helper.Argv("desc", default=""),)
def doc_post(title, source, desc):
    creator = session_helper.get_uid()
    if not user_service.query_user_meta(creator):
        raise exception.AppMissingUser()

    if not source.endswith(".zip"):
        raise exception.AppNotSupportSource()

    doc_id = doc_service.generate_doc_id()
    doc_service.post_doc(doc_id, title, source, desc, creator)
    return result.Result.simple(obj={"doc_id": doc_id})


@blue_print.route("/query", methods=["get", "post"])
@request_helper.param(
    request_helper.Argv("doc_id"),)
def query_doc(doc_id):
    item = doc_service.query_doc(doc_id)
    if not item:
        raise exception.AppMissingDoc()
    return result.Result.simple(obj=item)
