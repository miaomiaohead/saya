# -*- coding:utf-8 -*-

from webapp import protocol
from webapp.baselib import transaction
from tools.sql_builder import InsertBuilder, TotalBuilder, PageBuilder, SqlAND


@transaction.wrapper
async def list_doc(creator, status, start, limit, *, cursor):
    cond_dict = {}
    if creator:
        cond_dict["creator"] = creator
    if status:
        cond_dict["status"] = status

    cond = SqlAND(cond_dict)
    sql, args = TotalBuilder("docs", cond=cond).build()
    await cursor.execute(sql, args)
    res = await cursor.fetchone()
    total = int(res["total"])
    if not total:
        return protocol.Page.empty()
    columns = ['*']
    sql, args = PageBuilder("docs", columns, start, limit,
                            orderby="create_time", desc=True, cond=cond).build()
    await cursor.execute(sql, args)
    items = await cursor.fetchall()
    return protocol.Page(start, limit, total, items)


@transaction.wrapper
async def query_doc(doc_id, *, cursor):
    sql = "SELECT * FROM docs WHERE doc_id = %s"
    args = (doc_id,)
    await cursor.execute(sql, args)
    return await cursor.fetchone()


@transaction.wrapper
async def remove_doc(doc_id, *, cursor):
    sql = "DELETE FROM docs WHERE doc_id = %s"
    args = (doc_id,)
    await cursor.execute(sql, args)
    return await cursor.rowcount


@transaction.wrapper
async def insert_doc(doc_item, *, cursor):
    sql, args = InsertBuilder("docs", kvs=doc_item).build()
    await cursor.execute(sql, args)
    return await cursor.rowcount
