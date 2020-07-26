# -*- coding:utf-8 -*-

import aiohttp


class HttpClients(object):
    def __init__(self, loop):
        self._site_client_session = {}
        self._loop = loop

    def add_client(self, site, timeout=60):
        client_timeout = aiohttp.ClientTimeout(total=timeout)
        self._site_client_session[site] = aiohttp.ClientSession(timeout=client_timeout,
                                                                loop=self._loop)

    def get_client(self, site):
        return self._site_client_session[site]
