# -*- coding:utf-8 -*-


import functools

import aiomysql


def contain_cursor(kws):
    return True if isinstance(kws.get("cursor"), aiomysql.DictCursor) else False


def wrapper(f):
    """ transaction 自动承接事务，或创建事务
        装饰器自动创建connection和cursor
        若db函数调用关键词参数包含cursor，将会复用connection和cursor
    """
    @functools.wraps(f)
    async def inner(*ks, **kws):
        # 参数中包含cursor时，直接调用，使用传入的cursor进行处理
        if contain_cursor(kws):
            return await f(*ks, **kws)

        try:
            pool = kws["pool"]
        except KeyError:
            raise TypeError("missing required key-value argument: 'pool'")

        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                kws.update({
                    "cursor": cur,
                })
                kws.pop("pool")
                return await f(*ks, **kws)

    return inner

