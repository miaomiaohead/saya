# -*- coding:utf-8 -*-

from webapp.share import db_helper
from webapp.share.sql_builder import ReplaceBuilder


@db_helper.transaction
def query_user_meta(uid, *, cursor):
    sql = "SELECT * FROM users WHERE uid=%s"
    args = (uid,)
    cursor.execute(sql, args)
    return cursor.fetchone()


@db_helper.transaction
def query_user_meta_by_github_id(github_id, *, cursor):
    sql = "SELECT * FROM users WHERE github_id=%s"
    args = (github_id,)
    cursor.execute(sql, args)
    return cursor.fetchone()


@db_helper.transaction
def replace_user(user, *, cursor):
    sql, args = ReplaceBuilder("users", kvs=user).build()
    cursor.execute(sql, args)
    return cursor.fetchone()
