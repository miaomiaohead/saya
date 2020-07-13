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

    def update_doc_progress(self, doc_id, progress, status):
        cnx = self._db.connection()
        if not cnx:
            raise Exception("get db cnx failed")
        cursor = cnx.cursor(dictionary=True)
        if not cursor:
            raise Exception("get cursor failed")
        try:
            sql = "UPDATE docs SET progress = %s, status = %s WHERE doc_id = %s"
            args = (progress, status, doc_id)
            cursor.execute(sql, args)
        except Exception as e:
            cnx.rollback()
        else:
            cnx.commit()
        finally:
            cnx.close()
            cursor.close()

    def update_entry_url(self, doc_id, entry_url):
        cnx = self._db.connection()
        if not cnx:
            raise Exception("get db cnx failed")
        cursor = cnx.cursor(dictionary=True)
        if not cursor:
            raise Exception("get cursor failed")
        try:
            sql = "UPDATE docs SET url = %s WHERE doc_id = %s"
            args = (entry_url, doc_id)
            cursor.execute(sql, args)
        except Exception as e:
            cnx.rollback()
        else:
            cnx.commit()
        finally:
            cnx.close()
            cursor.close()

