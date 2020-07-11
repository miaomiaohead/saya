# -*- coding:utf-8 -*-

import uuid

from webapp import proto
from webapp.db import doc_db
from webapp.service import user_service


def generate_doc_id():
    return str(uuid.uuid4())


def list_doc(user, status, start, limit):
    page = doc_db.list_doc(user, status, start, limit)
    for item in page.items:
        creator = item["creator"]
        item["creator"] = user_service.query_user_meta(creator)
    return page


def remove_doc(doc_id):
    return doc_db.remove_doc(doc_id)


def post_doc(doc_id, title, source, desc, creator):
    doc_item = {
        "doc_id": doc_id,
        "title": title,
        "source": source,
        "desc": desc,
        "creator": creator,
        "status": proto.EnumDocStatus.WAIT,
        "progress": 0,
    }
    return doc_db.insert_doc(doc_item)


def query_doc_meta(doc_id):
    return doc_db.query_doc(doc_id)


def query_doc(doc_id):
    doc_item = query_doc_meta(doc_id)
    creator = doc_item["creator"]
    doc_item["creator"] = user_service.query_user_meta(creator)
    return doc_item
