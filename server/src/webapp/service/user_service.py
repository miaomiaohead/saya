# -*- coding:utf-8 -*-

from webapp.db import user_db


async def query_user_meta(request, uid):
    return await user_db.query_user_meta(uid, pool=request.app.db_pool)
