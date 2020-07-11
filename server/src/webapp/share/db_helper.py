# -*- coding:utf-8 -*-

import functools
from DBUtils import SteadyDB


def __contain_cursor__(kws):
    return True if isinstance(kws.get("cursor"), SteadyDB.SteadyDBCursor) else False


def __get_connection__(kws):
    """从关键词参数或flask.app中获得数据库连接
    """
    connection = kws.get("connection")
    if connection:
        return connection
    db_pool = kws.get("db_pool")
    if db_pool:
        return db_pool.connection()
    from flask import current_app as app
    return app.db_connect_pool.connection()


def transaction(f):
    """ transaction 自动承接事务，或创建事务
        装饰器自动创建connection和cursor
        若db函数调用关键词参数包含cursor，将会复用connection和cursor
    """
    @functools.wraps(f)
    def inner(*ks, **kws):
        # 参数中包含cursor时，直接调用，使用传入的cursor进行处理
        if __contain_cursor__(kws):
            return f(*ks, **kws)
        # 会话最外层的调用
        connection = __get_connection__(kws)
        cursor = connection.cursor(dictionary=True)
        kws["cursor"] = cursor
        kws["connection"] = connection
        kws["db_pool"] = None
        # 暂时不将connection/db_pool往下传递
        kws.pop("connection")
        kws.pop("db_pool")
        try:
            rv = f(*ks, **kws)
        except Exception as e:
            connection.rollback()
            raise e
        finally:
            connection.commit()
            cursor.close()
            connection.close()
        return rv
    return inner
