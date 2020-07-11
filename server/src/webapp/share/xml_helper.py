# -*- coding:utf-8 -*-

from bs4 import BeautifulSoup


class CData(object):
    """标记XML的CDATA数据
    """
    def __init__(self, value):
        self._v = value

    def value(self):
        return "<![CDATA[%s]]>" % self._v


def xml2dict(xml):
    """xml字符串转换为字典
    """
    soup = BeautifulSoup(xml, features='xml')
    xml = soup.find('xml')
    if not xml:
        return {}
    data = dict([(item.name, item.text) for item in xml.find_all()])
    return data


def dict2xml(data):
    """字典转xml字符串
    """
    xml = []
    for k in sorted(data.keys()):
        v = data.get(k)
        if v is None:
            continue
        if isinstance(v, CData):
            v = v.value()
        xml.append("<{key}>{value}</{key}>".format(key=k, value=v))
    return '<xml>{}</xml>'.format(''.join(xml))
