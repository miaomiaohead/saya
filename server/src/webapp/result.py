# -*- coding:utf-8 -*-


def __str2hump__(text):
    """驼峰转下划线
    """
    parts = text.lower().split('_')
    res = parts[0]
    for i in parts[1:]:
        res = res + i[0].upper() + i[1:]
    return res


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


def __make_json_response__(result):
    import json
    from flask import Response, current_app, g

    indent = None
    separators = (',', ':')
    # if current_app.config['JSONIFY_PRETTYPRINT_REGULAR'] or current_app.debug:
    #     indent = 2
    #     separators = (', ', ': ')
    # result = adapt_js(result)
    json_body = json.dumps(result,
                           default=lambda obj: obj.__dict__ if hasattr(obj, "__dict__") else str(obj),
                           indent=indent,
                           separators=separators,
                           ensure_ascii=False)
    response = Response(json_body, mimetype=current_app.config['JSONIFY_MIMETYPE'])
    if g.watcher.cookies:
        for k, v in g.watcher.cookies.items():
            response.set_cookie(k, v)
    return response


class Result(object):
    def __init__(self):
        self.__result__ = {}

    def set(self, key, val):
        self.__result__[str(key)] = val
        return self

    def done(self):
        self.__result__["success"] = True
        return __make_json_response__(self.__result__)

    @staticmethod
    def error(error_code, error_message):
        result = {
            "success": False,
            "error_code": int(error_code),
            "error_message": str(error_message)
        }
        return __make_json_response__(result)

    @staticmethod
    def simple(name="data", obj=None):
        result = {"success": True}
        if (obj is not None and
                name is not None):
            result[str(name)] = obj
        return __make_json_response__(result)

    @staticmethod
    def cdn_access_allow():
        resp = Result.simple()
        return resp

    @staticmethod
    def cdn_access_deny():
        from flask import make_response
        resp = make_response()
        return resp, 401
