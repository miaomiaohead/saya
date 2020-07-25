
# -*- coding:utf-8 -*-


# from tools.sql_builder import ReplaceBuilder

from webapp.baselib import transaction


@transaction.wrapper
async def query_user_meta(uid, *, cursor):
    sql = "SELECT * FROM users WHERE uid=%s"
    args = (uid,)
    await cursor.execute(sql, args)
    return await cursor.fetchone()
