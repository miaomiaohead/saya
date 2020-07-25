# -*- coding:utf-8 -*-

import aiomysql


async def create_db_pool(app, loop):
    pool = await aiomysql.create_pool(host=app.config.DATABASE_HOST,
                                      port=app.config.DATABASE_PORT,
                                      user=app.config.DATABASE_USER,
                                      password=app.config.DATABASE_PASSWORD,
                                      db=app.config.DATABASE_NAME,
                                      loop=loop)
    return pool
