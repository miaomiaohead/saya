# -*- coding:utf-8 -*-

import uuid

from webapp import protocol, exception
from webapp.service import user_service
from webapp.db import doc_db


def generate_doc_id():
    return str(uuid.uuid4())


async def list_doc(request, user, status, start, limit):
    page = await doc_db.list_doc(user, status, start, limit, pool=request.app.db_pool)
    for item in page.items:
        creator = item["creator"]
        item["creator"] = await user_service.query_user_meta(request, creator)
    return page


async def remove_doc(request, doc_id):
    return await doc_db.remove_doc(doc_id, pool=request.app.db_pool)


async def post_doc(request, doc_id, title, source, desc, creator):
    doc_item = {
        "doc_id": doc_id,
        "title": title,
        "source": source,
        "desc": desc,
        "creator": creator,
        "status": protocol.EnumDocStatus.WAIT,
        "progress": 0,
    }
    return await doc_db.insert_doc(doc_item, pool=request.app.db_pool)


async def query_doc_meta(request, doc_id):
    return await doc_db.query_doc(doc_id, pool=request.app.db_pool)


async def query_doc(request, doc_id):
    doc_item = await query_doc_meta(request, doc_id)
    if not doc_item:
        raise exception.AppMissingDoc()
    creator = doc_item["creator"]
    doc_item["creator"] = await user_service.query_user_meta(request, creator)
    return doc_item
