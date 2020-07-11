# -*- coding:utf-8 -*-

import sys
import json
import random
import time
import threading
import base64
import hashlib
from urllib import parse


def timestamp_format(timestamp=None, format_='%Y-%m-%d %H:%M:%S'):
    if timestamp is None:
        timestamp = time.time()
    time_tuple = time.localtime(timestamp)          # 把时间戳转换成时间元祖
    return time.strftime(format_, time_tuple)       # 把时间元祖转换成格式化好的时间


def json_loads(raw):
    try:
        return json.loads(raw)
    except:
        return None


def generate_randoms(size):
    alphabeta = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    return "".join(random.sample(alphabeta, size))


def dict2query(dic):
    query_parts = []
    for k, v in dic.items():
        query_parts.append("%s=%s" % (k, v))
    query_string = "&".join(query_parts)
    return query_string


def static_cast(type_function, origin, default=None):
    try:
        return type_function(origin)
    except:
        return default


def verify_url(url):
    url_detail = parse.urlparse(url)
    if not url_detail.scheme or not url_detail.netloc:
        return False
    return True


def sorted_dict(dic):
    if dic is None or not isinstance(dic, dict):
        return None
    ret = {}
    for k in sorted(dic.keys()):
        ret[k] = dic[k]
    return ret


def sha1(inp):
    """直接生成sha1
    """
    if isinstance(inp, str):
        inp = inp.encode("utf-8")
    sh1 = hashlib.sha1()
    sh1.update(inp)   
    return sh1.hexdigest()


def md5(inp):
    """直接生成md5
    """
    if isinstance(inp, str):
        inp = inp.encode("utf-8")
    md5lib = hashlib.md5()
    md5lib.update(inp)   
    return md5lib.hexdigest()


def urlsafe_b64encode(data):
    return str(base64.urlsafe_b64encode(data.encode("utf-8")), encoding="utf-8")


def urlsafe_b64decode(data):
    """解决b64的padding问题
    """
    try:
        missing_padding = 4 - len(data) % 4
        if missing_padding:
            data += '=' * missing_padding
        return str(base64.urlsafe_b64decode(data), encoding="utf-8")
    except:
        return None


def day_expire_timestamp(days):
    """返回第day天的23:59:59的秒级时间戳
    """
    if not isinstance(days, int):
        raise Exception("'days' parse error")
    after_day_timestamp = int(time.time() + days*3600*24)
    expire_date = time.strftime("%Y-%m-%d 23:59:59", time.localtime(after_day_timestamp))
    expire_timestamp = int(time.mktime(time.strptime(expire_date, "%Y-%m-%d %H:%M:%S")))
    return expire_timestamp


def incrementer_generator_fun(start):
    """线程安全的递增计数器
    """
    if not isinstance(start, int):
        raise Exception("parameterm 'start' not int")
    number = start
    lock = threading.Lock()
    while True:
        yield number
        lock.acquire()
        number += 1
        lock.release()


def line_info(pre=0):
    """获得行信息
    return [行所在文件名, 行所在函数, 行号]
    """
    f = sys._getframe(pre + 1)
    return [f.f_code.co_filename, f.f_code.co_name, f.f_lineno]


def format_str_to_list(s):
    if s is None or s == '':
        return None
    return s[1:-1].split("),(")


def format_list_to_str(l):
    if l is None or len(l) == 0:
        return None
    return "(%s)" % "),(".join([str(e) for e in sorted(l)])


class Watcher:
    """请求观察类, 该类用于观察请求的细节:
        * 请求的id
        * 请求的延时等
        * 请求的日志(请求共享该对象)
        * 请求的配置文件(请求共享该对象)
    """
    def __init__(self):
        self._create = time.time()
        self.static = False
        self.request_failed = False
        self.cookies = {}

    def delayed(self):
        """输出延时
        """
        now = time.time()
        return int((now - self._create) * 1000)

    def create(self):
        """当前请求时间戳
        """
        return self._create

    def ident(self):
        """请求标识
        """
        return id(self)

    def error(self, message):
        """记录错误
        """
        from flask import current_app as app
        line_file, line_fun, line_no = line_info(1)
        app.logger.error("[%s:%s():%s] [id = %s] %s" % (line_file,
                                                        line_fun, line_no, id(self), message))

    def info(self, message):
        """记录信息
        """
        from flask import current_app as app
        line_file, line_fun, line_no = line_info(1)
        app.logger.info("[%s:%s():%s] [id = %s] %s" % (line_file,
                                                       line_fun, line_no, id(self), message))

    def config(self, key):
        """获取配置文件
        """
        from flask import current_app as app
        return app.config[key]
