# -*- coding:utf-8 -*-

import os
import zipfile
import shutil

from concurrent import futures

def force_remove_dir(path):
    if not path:
        return
    shutil.rmtree(path=path)


def force_remove_path(path):
    if not path:
        return
    try:
        os.remove(path)
    except:
        pass


def unzip(path):
    temp_dir = os.path.dirname(path)
    zfile = zipfile.ZipFile(path, "r")
    for subfile in zfile.namelist(): 
        zfile.extract(subfile, temp_dir)
    zfile.close()


def find_sphinx_sourcedir(fromdir):
    import glob
    sourcedirs = glob.glob("**/index.rst", recursive=True)
    if not sourcedirs:
        return None
    return os.path.dirname(sourcedirs[0])


def sphinx_build(sourcedir, builddir):
    print("sourcedir: %s, builddir: %s" % ("sourcedir", builddir))

    abs_sourcedir = os.path.abspath(sourcedir)
    abs_builddir = os.path.abspath(builddir)

    previous_dir = os.getcwd()
    try:
        os.chdir(abs_sourcedir)
        command = "make html SOURCEDIR=%s BUILDDIR=%s" % (abs_sourcedir, abs_builddir)
        return os.popen(command).read()
    finally:
        os.chdir(previous_dir)


def dir_upload_kodo(local_dir, remote_dir, kodo_client, executor=None):
    if not executor:
        executor = futures.ThreadPoolExecutor(max_workers=1)

    if not local_dir or not os.path.exists(local_dir):
        raise Exception("local_dic(%s) not exists" % local_dir)

    def _upload(local_file, remote_file):
        kodo_client.upload(local_file, remote_file)
        return True, local_file, remote_file

    # 上传文件
    # 切换工作目录，因此该方法线程不安全
    sphinx_doc_entry = ""
    fs = []
    previous_dir = os.getcwd()
    try:
        os.chdir(local_dir)
        for root, dirs, files in os.walk("."):
            for f in files:
                local_file = "%s/%s" % (root, f)
                assert local_file.startswith("./")
                pretty_name = local_file[2:] # filter "./" prefix
                remote_file = "%s/%s" % (remote_dir, pretty_name)
                fs.append(executor.submit(_upload, local_file, remote_file))

                if "index.html" in remote_file and \
                        (not sphinx_doc_entry or len(sphinx_doc_entry) > len(remote_file)):
                    sphinx_doc_entry = remote_file

        # wait and print
        for ft in futures.as_completed(fs):
            print("upload", ft.result())

        return sphinx_doc_entry
    finally:
        os.chdir(previous_dir)


if __name__ == "__main__":
    import kodo

    QINIU_PUBLIC_STORE_REGION = "https://upload-z1.qiniup.com"
    QINIU_ACCESS_KEY = "sRd2-QgwgZnPgZyY1E6oS0QxtFWjGLNJwss9D2Op"
    QINIU_SECRET_KEY = "r4ZiD533tHlAzL9icthxkzjo1OD9PavzFQTLT7an"
    QINIU_PUBLIC_BUCKET = "saya-storage"

    kodo_client = kodo.KodoClient(QINIU_PUBLIC_STORE_REGION,
                                  QINIU_ACCESS_KEY,
                                  QINIU_SECRET_KEY,
                                  QINIU_PUBLIC_BUCKET)

    dir_upload_kodo("../../docs/_build/",
                    "user/aa0abdd5-4d5a-460d-b3ca-8a70e27469d7/test-doc",
                    kodo_client)
