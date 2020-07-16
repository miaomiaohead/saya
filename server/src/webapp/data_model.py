# -*- coding:utf-8 -*-


class Page(object):
    """
    """
    def __init__(self, start, limit, total, items):
        #: 数据偏移
        self.start = start
        #: 数据个数限制
        self.limit = limit
        #: 总共的数据量
        self.total = total
        #: 数据元素的列表
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


class Document(Base):
    def __init__(self):
        pass