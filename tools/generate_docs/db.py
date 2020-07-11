# -*- coding:utf-8 -*-

import mysql.connector
from DBUtils.PersistentDB import PersistentDB


class DbClient(object):
    def __init__(self, host, port, db, user, password):
        self._db = PersistentDB(mysql.connector,
                                host=host,
                                user=user,
                                passwd=password,
                                db=db,
                                port=port)

    def list_docs(self, limit):
        cnx = self._db.connection()
        if not cnx:
            raise Exception("get db cnx failed")
        cursor = cnx.cursor(dictionary=True)
        if not cursor:
            raise Exception("get cursor failed")
        try:
            sql = "SELECT doc_id, creator, title, source FROM docs WHERE status = %s LIMIT %s"
            args = ("WAIT", limit)
            cursor.execute(sql, args)
            return cursor.fetchall()
        finally:
            cnx.close()
            cursor.close()

