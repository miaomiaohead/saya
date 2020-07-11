# -*- coding:utf-8 -*-

import functools
from werkzeug.contrib.cache import SimpleCache
from flask import current_app as app


def local_cache(timeout=60, cache_size=10000, logger=None):
    """ 本地缓存, 每个local_cache之间隔离缓存
    暂不支持命名参数
    """
    lc = SimpleCache(threshold=cache_size, default_timeout=timeout)

    def inner(f):
        @functools.wraps(f)
        def wrapper(*ks, _cache=False, **kws):
            if not _cache:
                return f(*ks, **kws)
            # 仅仅支持str, int ,float, list类型的参数
            function_name = getattr(f, "__name__")
            nks = [function_name]
            for k, v in kws.items():
                if not isinstance(k, str) or not isinstance(v, (str, int, float)):
                    if logger:
                        logger.warning("cache parameter type invalid")
                    return f(*ks, **kws)
                nks.append("%s:%s" % (k, v))
            for k in ks:
                if not isinstance(k, (str, int, float, list)):
                    if logger:
                        logger.warning("cache parameter type invalid")
                    return f(*ks, **kws)
                nks.append(str(k))
            link_ks = "-".join(nks)
            result = lc.get(link_ks)
            if result is not None:
                app.statistic_helper.append_record("HIT_CACHE", function_name, 1)
                return result
            else:
                app.statistic_helper.append_record("HIT_CACHE", function_name, 0)
                result = f(*ks, **kws)
                lc.set(link_ks, result, timeout=timeout)
                return result
        return wrapper
    return inner
