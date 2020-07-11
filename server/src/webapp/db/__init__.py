# -*- coding:utf-8 -*-
"""
db初始化，主要是创建服务器到数据源的连接
* redis连接
* mysql连接
* elastic_search连接
"""

import redis
import mysql.connector
from DBUtils.PersistentDB import PersistentDB
from elasticsearch import Elasticsearch


def create_elastic_cli(auth, nodes):
    """创建es客户端连接
    """
    args = {"use_ssl": False}
    if auth:
        args["http_auth"] = auth
    es_cli = Elasticsearch(nodes, **args)
    return es_cli


def create_redis_cli(host, port, password, db):
    """创建redis客户端连接
    """
    redis_pool = redis.ConnectionPool(host=host,
                                      port=port,
                                      password=password,
                                      db=db)
    redis_cli = redis.Redis(connection_pool=redis_pool)
    return redis_cli


def create_connect_pool(host, user, password, db, port=3306, ping=1):
    """创建MySQL数据库连接池对象
    """
    connect_pool = PersistentDB(mysql.connector,
                                host=host,
                                user=user,
                                passwd=password,
                                db=db,
                                port=port,
                                ping=ping)
    return connect_pool
