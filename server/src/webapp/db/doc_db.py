# -*- coding:utf-8 -*-

from webapp import data_model
from webapp.share import db_helper
from webapp.share.sql_builder import InsertBuilder, TotalBuilder, PageBuilder, SqlAND


@db_helper.transaction
def list_doc(creator, status, start, limit, *, cursor):
    cond_dict = {}
    if creator:
        cond_dict["creator"] = creator
    if status:
        cond_dict["status"] = status

    cond = SqlAND(cond_dict)
    sql, args = TotalBuilder("docs", cond=cond).build()
    cursor.execute(sql, args)
    total = int(cursor.fetchone()["total"])
    if not total:
        return data_model.Page.empty()
    columns = ['*']
    sql, args = PageBuilder("docs", columns, start, limit,
                            orderby="create_time", desc=True, cond=cond).build()
    cursor.execute(sql, args)
    items = cursor.fetchall()
    return data_model.Page(start, limit, total, items)


@db_helper.transaction
def query_doc(doc_id, *, cursor):
    sql = "SELECT * FROM docs WHERE doc_id = %s"
    args = (doc_id,)
    cursor.execute(sql, args)
    return cursor.fetchone()


@db_helper.transaction
def remove_doc(doc_id, *, cursor):
    sql = "DELETE FROM docs WHERE doc_id = %s"
    args = (doc_id,)
    cursor.execute(sql, args)
    return cursor.rowcount


@db_helper.transaction
def insert_doc(doc_item, *, cursor):
    sql, args = InsertBuilder("docs", kvs=doc_item).build()
    cursor.execute(sql, args)
    return cursor.rowcount
