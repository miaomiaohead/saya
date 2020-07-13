# -*- coding:utf-8 -*-

import os
from concurrent import futures

import requests
import kodo, db, tools


HANDLE_LIMIT = 1000

SAYA_CDN_HOST = "http://cdn.saya.signalping.com"

QINIU_PUBLIC_STORE_REGION = "https://upload-z1.qiniup.com"
QINIU_ACCESS_KEY = "sRd2-QgwgZnPgZyY1E6oS0QxtFWjGLNJwss9D2Op"
QINIU_SECRET_KEY = "r4ZiD533tHlAzL9icthxkzjo1OD9PavzFQTLT7an"
QINIU_PUBLIC_BUCKET = "saya-storage"


DB_HOST = "saya.signalping.com"
DB_PORT = 3309
DB_NAME = "saya_db"
DB_USER = "root"
DB_PAWD = "root@saya"


def download_from_source(doc, timeout):
    local_path = None
    try:
        doc_id = doc["doc_id"]
        creator = doc["creator"]
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
        tools.force_remove_path(local_path)
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

        # 主线程对文档进行解压
        # 解压目录为 temp/${doc_id}/doc/
        print(os.getcwd())
        for fut in futures.as_completed(future_to_doc):
            success, data = fut.result()
            doc = future_to_doc[fut]
            source = doc["source"]
            doc_id = doc["doc_id"]
            creator = doc["creator"]
            package_path = data

            print("==================================")
            print(success, " : ", data)
            if not success:
                # 下载失败
                db_client.update_doc_progress(doc_id, 100, "FAILED")
                continue
            db_client.update_doc_progress(doc_id, 10, "WAIT")

            # 解压并成功
            tools.unzip(package_path)
            db_client.update_doc_progress(doc_id, 30, "WAIT")

            # 寻找 sphinx 的 source 目录
            sphinx_sourcedir = tools.find_sphinx_sourcedir(os.path.dirname(package_path))
            if not sphinx_sourcedir:
                # 无法找到 sourcedir
                db_client.update_doc_progress(doc_id, 100, "FAILED")
                continue
            db_client.update_doc_progress(doc_id, 40, "WAIT")

            # 文档生成
            sphinx_builddir = "%s/_build" % sphinx_sourcedir
            build_message = tools.sphinx_build(sphinx_sourcedir, sphinx_builddir)
            db_client.update_doc_progress(doc_id, 60, "WAIT")

            # 多线程上传文件
            param = {"creator": creator, "doc_id": doc_id}
            remotedir = "user/{creator}/{doc_id}".format(**param)
            entry = tools.dir_upload_kodo(sphinx_builddir, remotedir, kodo_client)
            entry_url = "%s/%s" % (SAYA_CDN_HOST, entry)
            print("doc entry_url: %s" % entry_url)

            # 删除本地目录
            print(os.getcwd())
            tools.force_remove_dir("./temp")
            db_client.update_doc_progress(doc_id, 100, "SUCCESS")
            db_client.update_entry_url(doc_id, entry_url)

def main():
    App().run()


if __name__ == "__main__":
    main()
