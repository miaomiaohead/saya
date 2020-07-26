
# -*- coding:utf-8 -*-


from tools.sql_builder import ReplaceBuilder

from webapp.baselib import transaction


@transaction.wrapper
async def query_user_meta(uid, *, cursor):
    sql = "SELECT * FROM users WHERE uid=%s"
    args = (uid,)
    await cursor.execute(sql, args)
    return await cursor.fetchone()


@transaction.wrapper
async def query_user_meta_by_github_id(github_id, *, cursor):
    sql = "SELECT * FROM users WHERE github_id=%s"
    args = (github_id,)
    await cursor.execute(sql, args)
    return await cursor.fetchone()


@transaction.wrapper
async def replace_user(user, *, cursor):
    sql, args = ReplaceBuilder("users", kvs=user).build()
    await cursor.execute(sql, args)
    return await cursor.rowcount
