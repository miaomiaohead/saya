# -*- coding:utf-8 -*-

from sanic.response import HTTPResponse


def __str2hump__(text):
    """驼峰转下划线
    """
    parts = text.lower().split('_')
    res = parts[0]
    for i in parts[1:]:
        res = res + i[0].upper() + i[1:]
    return res


def adapt_js_array(array):
    """列表和元组转驼峰
    """
    js_array = []
    for item in array:
        js_array.append(adapt_js(item))
    return js_array


def adapt_js(obj):
    if isinstance(obj, list):
        return adapt_js_array(obj)
    elif isinstance(obj, tuple):
        return adapt_js_array(obj)
    return adapt_js_dict(obj)


def adapt_js_dict(obj):
    """字典和对象转驼峰字典
    """
    py_dict = None
    if isinstance(obj, dict):
        py_dict = obj
    if hasattr(obj, "__dict__"):
        py_dict = obj.__dict__
    if py_dict is None:
        return obj
    js_dict = {}
    for k, v in py_dict.items():
        js_key = __str2hump__(str(k))
        js_dict[js_key] = adapt_js(v)
    return js_dict


def make_json_response(dic, headers=None, status=200, content_type="application/json",):
    import json
    indent = None
    separators = (',', ':')
    json_body = json.dumps(dic,
                           default=lambda obj: obj.__dict__ if hasattr(obj, "__dict__") else str(obj),
                           indent=indent,
                           separators=separators,
                           ensure_ascii=False)
    resp = HTTPResponse(json_body,
                        headers=headers,
                        status=status,
                        content_type=content_type,)
    return resp


class Result(object):
    def __init__(self):
        self._result = {}

    def set(self, key, val):
        self._result[str(key)] = val
        return self

    def done(self):
        from sanic.response import json

        self._result["success"] = True
        return json(self._result, ensure_ascii=False)

    @staticmethod
    def simple(name="data", obj=None):
        result = {"success": True}
        if (obj is not None and
                name is not None):
            result[str(name)] = obj
        return make_json_response(result)

    @staticmethod
    def obj(obj=None):
        return make_json_response(obj)
