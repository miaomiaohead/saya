# -*- coding:utf-8 -*-


class Page(object):
    def __init__(self, start, limit, total, items):
        self.start = start
        self.limit = limit
        self.total = total
        self.items = items

    @staticmethod
    def empty():
        return Page(0, 0, 0, [])

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)


class Base(object):
    def link_fields(self, table_name=None):
        if table_name is None:
            table_name = ""
        if table_name:
            table_name = table_name + "."
        keys = ["%s%s" % (table_name, key) for key in self.__dict__.keys()]
        return ",".join(keys)
