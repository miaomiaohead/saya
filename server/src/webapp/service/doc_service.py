# -*- coding:utf-8 -*-

import uuid

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
