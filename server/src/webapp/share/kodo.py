# -*- coding:utf-8 -*-

import time
import json
import hmac
import hashlib
import requests
import tempfile
from urllib.parse import urlparse
from base64 import urlsafe_b64encode


def _b(data):
    if isinstance(data, str):
        return data.encode('utf-8')
    return data


def _s(data):
    if isinstance(data, bytes):
        data = data.decode('utf-8')
    return data


def urlsafe_base64_encode(data):
    ret = urlsafe_b64encode(_b(data))
    return _s(ret)


class KodoClient(object):
    """七牛云客户端
    """
    __list_host__ = "rsf.qbox.me"
    __delete_host__ = "rs.qiniu.com"
    __batch_host__ = "rs.qiniu.com"

    def __init__(self, store_region, access_key, secret_key, bucket):
        self._tool = KodoTools(store_region, access_key, secret_key, bucket)

    def manager_token(self, url, body=None):
        """管理凭证
        """
        return self._tool.manager_token(url, body)

    def upload_token(self, path=None, expire=3600):
        """上传凭证
        """
        return self._tool.upload_token(path, expire)

    def download_token(self, download_url, expire=60):
        """下载凭证
        """
        return self._tool.download_token(download_url, expire)

    def upload(self, local, path=None, token=None):
        """上传本地文件到kodo
            local : 本地文件路径
            path : kodo文件名
        """
        if not token:
            token = self._tool.upload_token(path)
        param = {"token": token, }
        if path is not None:
            param["key"] = path
        with open(local, "rb") as local_file:
            files = {'file': local_file}
            r = requests.post(self._tool._store_region, data=param, files=files)
            r.encoding = "utf-8"
            success = r.status_code == 200
            message = ""
            if r.status_code != 200:
                message = r.text
            return success, message

    def upload_rb(self, local, path=None):
        """上传本地文件到KODO
            local : 本地文件(已经用rb打开)
            path : kodo文件名
        """
        token = self._tool.kodo_upload_token(path)
        param = {"token": token, }
        if path is not None:
            param["key"] = path
        files = {'file': local}
        r = requests.post(self._tool._store_region, data=param, files=files)
        r.encoding = "utf-8"
        success = r.status_code == 200
        message = ""
        if r.status_code != 200:
            message = r.text
        return success, message

    def upload_from_remote(self, remote, path=None):
        """将互联网文件上传到KODO
            remote : 远程文件url
            path : kodo文件名
        """
        temp = None
        try:
            temp = tempfile.TemporaryFile()
            r = requests.get(remote)
            temp.write(r.content)
            temp.seek(0, 0)
            return self.upload_rb(temp, path)
        finally:
            if temp is not None:
                temp.close()

    def list_once(self, marker=''):
        """迭代一次文件列表
            marker:迭代偏移
        """
        url = "http://%s/list?bucket=%s" % (self.__list_host__, self._tool._bucket)
        if marker:
            url += "&marker=" + marker
        access_token = self._tool.manager_token(url)
        headers = {
            "Host": self.__list_host__,
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "QBox " + access_token,
        }
        r = requests.get(url, headers=headers)
        r.encoding = "utf-8"
        if r.status_code != 200:
            return None, r.text
        rjson = r.json()
        next_marker = rjson.get("marker")
        items = rjson.get("items")
        paths = [item["key"] for item in items]
        return paths, next_marker

    def list_full(self):
        """列出所有文件
        """
        paths = []
        marker = ""
        while True:
            path_parts, marker = self.list_once(marker)
            if path_parts is None:
                continue
            paths += path_parts
            if not marker:
                return paths

    def delete(self, path):
        """删除文件
        """
        encoded_entry_uri = self._tool.encode_entry(path)
        url = "http://%s/delete/%s" % (self.__delete_host__, encoded_entry_uri)
        access_token = self._tool.manager_token(url)
        headers = {
            "Host": self.__delete_host__,
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "QBox " + access_token,
        }
        r = requests.post(url, headers=headers)
        r.encoding = "utf-8"
        success = r.status_code == 200
        message = ""
        if r.status_code != 200:
            message = r.text
        return success, message

    def batch_delete(self, paths):
        """批量清除
        """
        if paths is None or len(paths) == 0:
            return False, "empty paths"
        url = "http://%s/batch" % self.__batch_host__
        dels = ["op=/delete/%s" % self._tool.encode_entry(path) for path in paths]
        body = "&".join(dels)
        access_token = self._tool.manager_token(url, body)
        headers = {
            "Host": self.__batch_host__,
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "QBox " + access_token,
        }
        r = requests.post(url, data=body, headers=headers)
        r.encoding = "utf-8"
        success = r.status_code == 200
        message = ""
        if r.status_code != 200:
            message = r.text
        return success, message

    def clear(self):
        """清空bucket
        """
        paths = self.list_full()
        return self.batch_delete(paths)


class KodoTools:
    def __init__(self, store_region, access_key, secret_key, bucket):
        self._store_region = store_region
        self._access_key = access_key
        self._secret_key = secret_key
        self._bucket = bucket

    def __encode_sign(self, data):
        """生成base64编码的签名:
            sign = token(data) = hmac_sha1(secret_key, data)
            encode_sign = urlsafe_base64_encode(sign)
        """
        data = _b(data)
        secret_key = _b(self._secret_key)
        hashed = hmac.new(secret_key, data, hashlib.sha1)
        return urlsafe_base64_encode(hashed.digest())

    def encode_entry(self, path):
        entry = '%s:%s' % (self._bucket, path)
        encoded_entry_uri = urlsafe_base64_encode(entry)
        return encoded_entry_uri

    def manager_token(self, url, body=None):
        """管理凭证:
            data = "<path>?<query>\n<body>"
            sign = token(data) = hmac_sha1(secret_key, data)
            encoded_sign = urlsafe_base64_encode(sign)
            access_token = "<access_key>:<encode_sign>"
        """
        parsed_url = urlparse(url)
        query = parsed_url.query
        path = parsed_url.path
        data = "%s?%s" % (path, query) if query else path
        data += "\n"
        if body:
            data += body
        access_key = self._access_key
        encoded_sign = self.__encode_sign(data)
        return '%s:%s' % (access_key, encoded_sign)

    def upload_token(self, path=None, expire=3600):
        """上传凭证:
            policy = {}
            data = encode_policy = urlsafe_base64_encode(policy)
            sign = hmac_sha1(secret_key, data)
            encoded_sign = urlsafe_base64_encode(sign)
            upload_token = "<AccessKey>:<encoded_sign>:<encode_policy>"
        """
        bucket = self._bucket
        scope = bucket
        if path is not None:
            scope = "%s:%s" % (bucket, path)
        policy = {
            "scope": scope,
            "deadline": int(time.time()) + expire,
            "isPrefixalScope": 1,
        }
        policy_json = json.dumps(policy, separators=(',', ':'))
        encoded_policy = urlsafe_base64_encode(policy_json)
        data = encoded_policy
        encoded_sign = self.__encode_sign(data)
        access_key = self._access_key
        return "%s:%s:%s" % (access_key, encoded_sign, encoded_policy)

    def download_token(self, download_url=None, expire=60):
        """下载凭证
        """
        deadline = int(time.time()) + expire
        download_url = "%s?e=%s" % (download_url, deadline)
        sign = self.__encode_sign(download_url)
        token = "%s:%s" % (self._access_key, sign)
        return token, deadline
