# -*- coding:utf-8 -*-

import kodo


LOCAL_FILE = "saya.zip"
UPLOAD_PREFIX = "user/aa0abdd5-4d5a-460d-b3ca-8a70e27469d7/"
UPLOAD_FILE = "asfasdcds.zip"

QINIU_PUBLIC_STORE_REGION = "https://upload-z1.qiniup.com"
QINIU_ACCESS_KEY = "sRd2-QgwgZnPgZyY1E6oS0QxtFWjGLNJwss9D2Op"
QINIU_SECRET_KEY = "r4ZiD533tHlAzL9icthxkzjo1OD9PavzFQTLT7an"
QINIU_PUBLIC_BUCKET = "saya-storage"


def main():
    # 七牛云对象存储
    kodo_client = kodo.KodoClient(QINIU_PUBLIC_STORE_REGION,
                                  QINIU_ACCESS_KEY,
                                  QINIU_SECRET_KEY,
                                  QINIU_PUBLIC_BUCKET)
    REMOTE_FILE_PATH = "%s%s" % (UPLOAD_PREFIX, UPLOAD_FILE)
    token = kodo_client.upload_token(path=UPLOAD_PREFIX)
    print(kodo_client.upload(local=LOCAL_FILE, path=REMOTE_FILE_PATH, token=token))


if __name__ == "__main__":
    main()
