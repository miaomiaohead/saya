# -*- coding:utf-8 -*-

import os
from concurrent import futures

import requests
import kodo
import db
import unpack

HANDLE_LIMIT = 1000

QINIU_PUBLIC_STORE_REGION = "https://upload-z1.qiniup.com"
QINIU_ACCESS_KEY = "sRd2-QgwgZnPgZyY1E6oS0QxtFWjGLNJwss9D2Op"
QINIU_SECRET_KEY = "r4ZiD533tHlAzL9icthxkzjo1OD9PavzFQTLT7an"
QINIU_PUBLIC_BUCKET = "saya-storage"


DB_HOST = "saya.signalping.com"
DB_PORT = 3309
DB_NAME = "saya_db"
DB_USER = "root"
DB_PAWD = "root@saya"

def force_remove_dir(path):
    if not path:
        return
    try:
        os.removedirs(path)
    except:
        pass


def force_remove_path(path):
    if not path:
        return
    try:
        os.remove(path)
    except:
        pass


def download_from_source(doc, timeout):
    local_path = None
    try:
        doc_id = doc["doc_id"]
        creator = doc["source"]
        source = doc["source"]

        # 发请求
        r = requests.get(source, timeout=timeout)

        # 写磁盘
        local_path = "temp/{doc_id}/x_doc.package".format(doc_id=doc_id)
        if not os.path.exists(os.path.dirname(local_path)):
            os.makedirs(os.path.dirname(local_path))
        with open(local_path, "wb") as f:
            f.write(r.content)

        return True, local_path
    except Exception as e:
        force_remove_path(local_path)
        return False, e


class App(object):
    def __init__(self):
        self.db_client = db.DbClient(DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PAWD)
        self.kodo_client = kodo.KodoClient(QINIU_PUBLIC_STORE_REGION,
                                           QINIU_ACCESS_KEY,
                                           QINIU_SECRET_KEY,
                                           QINIU_PUBLIC_BUCKET)

    def run(self):
        db_client = self.db_client
        kodo_client = self.kodo_client
        network_executor = futures.ThreadPoolExecutor(max_workers=8)

        docs = db_client.list_docs(HANDLE_LIMIT)
        print("download docs size: ", len(docs))

        # 多线程下载文档
        future_to_doc = dict(
            (network_executor.submit(download_from_source, doc, 60), doc)
             for doc in docs)

        # 主线程对文档进行解压并
        for fut in futures.as_completed(future_to_doc):
            success, data = fut.result()
            print("==================================")
            print(success, data)
            if not success:
                continue
            doc = future_to_doc[fut]
            source = doc["source"]
            unpack.unzip(data)


def main():
    App().run()


if __name__ == "__main__":
    main()
