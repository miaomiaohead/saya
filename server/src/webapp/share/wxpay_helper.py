# -*- coding:utf-8 -*-

import hashlib
import random
import time

import requests
from webapp.share import xml_helper

_UNIFIED_ORDER_URL = "https://api.mch.weixin.qq.com/pay/unifiedorder"
_QUERY_ORDER_URL = "https://api.mch.weixin.qq.com/pay/orderquery"
_CLOSE_ORDER_URL = "https://api.mch.weixin.qq.com/pay/closeorder"
_DOWNLOAD_BILL_URL = "https://api.mch.weixin.qq.com/pay/downloadbill"


class BaseRequest(object):
    def usage_dict(self):
        """过滤None的属性, 根据key排序
        """
        ud = {}
        for k in sorted(self.__dict__.keys()):
            v = self.__dict__[k]
            if v is None:
                continue
            ud[k] = v
        return ud

    def __str__(self):
        """直接输出所有属性
        """
        return str(self.__dict__)


class DownloadBillRequest(BaseRequest):
    """下载对账单
    """
    def __init__(self, appid, mch_id, nonce_str, sign, bill_date, bill_type, tar_type):
        self.appid = appid
        self.mch_id = mch_id
        self.nonce_str = nonce_str
        self.sign = sign
        self.bill_date = bill_date
        self.bill_type = bill_type
        self.tar_type = tar_type


class CloseOrderRequest(BaseRequest):
    """关闭订单
    """
    def __init__(self, appid, mch_id, nonce_str, sign, out_trade_no):
        self.appid = appid
        self.mch_id = mch_id
        self.nonce_str = nonce_str
        self.sign = sign
        self.out_trade_no = out_trade_no


class QueryOrderRequest(BaseRequest):
    """查询订单请求
    """
    def __init__(self, appid, mch_id, nonce_str, sign, out_trade_no):
        self.appid = appid
        self.mch_id = mch_id
        self.nonce_str = nonce_str
        self.sign = sign
        self.out_trade_no = out_trade_no


class UnifiedOrderRequest(BaseRequest):
    """统一下单模型
    """
    def __init__(self, appid, mch_id, nonce_str, sign, body, out_trade_no,
                 total_fee, spbill_create_ip, notify_url, trade_type, **kvs):
        # 必选字段
        self.appid = appid
        self.mch_id = mch_id
        self.nonce_str = nonce_str
        self.sign = sign
        self.body = body
        self.out_trade_no = out_trade_no
        self.total_fee = total_fee
        self.spbill_create_ip = spbill_create_ip
        self.notify_url = notify_url
        self.trade_type = trade_type
        if trade_type == "JSAPI" and "openid" not in kvs:
            message = "missing 1 required argument: 'openid' when trade_type='JSAPI'"
            raise TypeError(message)
        # 可选字段
        self.device_info = kvs.get("device_info")
        self.sign_type = kvs.get("sign_type")
        self.detail = kvs.get("detail")
        self.attach = kvs.get("attach")
        self.fee_type = kvs.get("fee_type")
        self.time_start = kvs.get("time_start")
        self.time_expire = kvs.get("time_expire")
        self.goods_tag = kvs.get("goods_tag")
        self.product_id = kvs.get("product_id")
        self.limit_pay = kvs.get("limit_pay")
        self.openid = kvs.get("openid")
        self.receipt = kvs.get("receipt")
        self.scene_info = kvs.get("scene_info")


class WechatPayHelper(object):
    """微信支付工具
    """

    def __init__(self, appid, mch_id, key):
        self._appid = appid
        self._mch_id = mch_id
        self._key = key

    def unifiedorder(self, body, out_trade_no, total_fee,
                     spbill_create_ip, notify_url, openid):
        """统一下单请求
        """
        unified_order_request = self.generate_unified_order_request(
                                        body, out_trade_no, total_fee,
                                        spbill_create_ip, notify_url, trade_type='JSAPI', openid=openid)
        return self.call_wxpay(_UNIFIED_ORDER_URL, unified_order_request)

    def downloadbill(self, bill_date, bill_type="ALL", tar_type=None):
        """下载对账单
        """
        download_bill_request = self.generate_download_bill_request(bill_date,
                                                                    bill_type=bill_type,
                                                                    tar_type=tar_type)
        return self.call_wxpay(_DOWNLOAD_BILL_URL, download_bill_request, raw=True)

    def queryorder(self, out_trade_no):
        """查询订单状态
        """
        query_order_request = self.generate_query_order_request(out_trade_no)
        return self.call_wxpay(_QUERY_ORDER_URL, query_order_request)

    def closeorder(self, out_trade_no):
        """关闭订单
        """
        close_order_request = self.generate_close_order_request(out_trade_no)
        return self.call_wxpay(_CLOSE_ORDER_URL, close_order_request)

    def jsapi_unifiedorder(self, body, out_trade_no, total_fee, spbill_create_ip,
                           notify_url, openid, trade_type):
        """jsapi 统一下单请求
        """
        if trade_type != "JSAPI":
            raise NotImplementedError("not support '%s'" % trade_type)
        unified_order_request = self.generate_unified_order_request(body,
                                                                    out_trade_no,
                                                                    total_fee,
                                                                    spbill_create_ip,
                                                                    notify_url,
                                                                    trade_type,
                                                                    openid=openid)
        return self.call_wxpay(_UNIFIED_ORDER_URL, unified_order_request)

    def native_unifiedorder(self, body, out_trade_no, total_fee, spbill_create_ip,
                            notify_url, trade_type, product_id):
        """native 统一下单请求
        """
        if trade_type != "NATIVE":
            raise NotImplementedError("not support '%s'" % trade_type)
        unified_order_request = self.generate_unified_order_request(body,
                                                                    out_trade_no,
                                                                    total_fee,
                                                                    spbill_create_ip,
                                                                    notify_url,
                                                                    trade_type,
                                                                    product_id=product_id)
        return self.call_wxpay(_UNIFIED_ORDER_URL, unified_order_request)

    def call_wxpay(self, url, request, raw=False):
        """发送微信请求
        """
        request_body = xml_helper.dict2xml(request.usage_dict())
        response = requests.post(url, data=request_body.encode("utf-8"))
        response.encoding = "utf-8"
        return response.text if raw else xml_helper.xml2dict(response.text)

    def generate_download_bill_request(self, bill_date, bill_type, tar_type):
        """生成下载对账单请求
        """
        nonce_str = md5(str(random.random())).upper()
        pre_sign = None
        download_bill_request = DownloadBillRequest(self._appid,
                                                    self._mch_id,
                                                    nonce_str,
                                                    pre_sign,
                                                    bill_date,
                                                    bill_type,
                                                    tar_type)
        sign = self._sign(download_bill_request.usage_dict(), self._key)
        download_bill_request.sign = sign
        return download_bill_request

    def generate_close_order_request(self, out_trade_no):
        """生成关闭订单请求
        """
        nonce_str = md5(str(random.random())).upper()
        pre_sign = None
        close_order_request = QueryOrderRequest(self._appid,
                                                self._mch_id,
                                                nonce_str,
                                                pre_sign,
                                                out_trade_no)
        sign = self._sign(close_order_request.usage_dict(), self._key)
        close_order_request.sign = sign
        return close_order_request

    def generate_query_order_request(self, out_trade_no):
        """生成查询订单请求
        """
        nonce_str = md5(str(random.random())).upper()
        pre_sign = None
        query_order_request = QueryOrderRequest(self._appid,
                                                self._mch_id,
                                                nonce_str,
                                                pre_sign,
                                                out_trade_no)
        sign = self._sign(query_order_request.usage_dict(), self._key)
        query_order_request.sign = sign
        return query_order_request

    def generate_unified_order_request(self, body, out_trade_no, total_fee,
                                       spbill_create_ip, notify_url, trade_type, **kvs):
        """生成统一下单数据结构
        """
        nonce_str = md5(str(random.random())).upper()
        pre_sign = None
        order_request = UnifiedOrderRequest(self._appid,
                                            self._mch_id,
                                            nonce_str,
                                            pre_sign,
                                            body,
                                            out_trade_no,
                                            total_fee,
                                            spbill_create_ip,
                                            notify_url,
                                            trade_type,
                                            **kvs)
        sign = self._sign(order_request.usage_dict(), self._key)
        order_request.sign = sign
        return order_request

    def generate_jsapi_pay_request(self, prepay_id):
        """生成JSAPI拉起微信支付需要的参数
        """
        timestamp = int(time.time())
        nonce_str = md5(str(random.random())).upper()
        package = 'prepay_id=%s' % prepay_id
        appid = self._appid
        sign_type = 'MD5'
        dic = {
            'appId': appid,
            'timeStamp': timestamp,
            'nonceStr': nonce_str,
            'package': package,
            'signType': sign_type
        }
        pay_sign = self._sign(dic, self._key)
        dic['paySign'] = pay_sign
        return dic

    def generate_applets_pay_request(self, prepay_id):
        """生成小程序拉起微信支付需要的参数
        """
        timestamp = int(time.time())
        nonce_str = md5(str(random.random())).upper()
        package = 'prepay_id=%s' % prepay_id
        appid = self._appid
        sign_type = 'MD5'
        dic = {'appId': appid, 'timeStamp': timestamp, 'nonceStr': nonce_str, 'package': package, 'signType': sign_type}
        pay_sign = self._sign(dic, self._key)
        dic['paySign'] = pay_sign
        return dic

    def notify_sign_check(self, request):
        xml = request.data
        dic = xml_helper.xml2dict(xml)

        sign = dic.get('sign')
        if sign is None:
            return False

        appid = dic.get('appid')
        mch_id = dic.get('mch_id')
        nonce_str = dic.get('nonce_str')
        result_code = dic.get('result_code')
        openid = dic.get('openid')
        is_subscribe = dic.get('is_subscribe')
        trade_type = dic.get('trade_type')
        bank_type = dic.get('bank_type')
        total_fee = dic.get('total_fee')
        cash_fee = dic.get('cash_fee')
        transaction_id = dic.get('transaction_id')
        out_trade_no = dic.get('out_trade_no')
        time_end = dic.get('time_end')

        if appid is None or \
                mch_id is None or \
                nonce_str is None or \
                result_code is None or \
                openid is None or \
                is_subscribe is None or \
                trade_type is None or \
                bank_type is None or \
                total_fee is None or \
                cash_fee is None or \
                transaction_id is None or \
                out_trade_no is None or \
                time_end is None:
            return False

        if trade_type != 'JSAPI' and trade_type != "NATIVE":
            return False

        sign_type = dic.get('sign_type')
        if sign_type == 'HMAC-SHA256':
            return False

        if appid != self._appid or mch_id != self._mch_id:
            return False

        dic_cp = dic.copy()
        dic_cp.pop('sign')
        cal_sign = self._sign(dic_cp, self._key)

        if sign != cal_sign:
            return False

        return dic

    def _sign(self, dic, key=None):
        """输入数字 计算起签名
        """
        if key is None:
            key = self._key
        kvs = []
        for k in sorted(dic.keys()):
            v = dic[k]
            kvs.append("%s=%s" % (k, v))
        encoded_kvs = "&".join(kvs)
        sign_temp = "%s&key=%s" % (encoded_kvs, key)
        signed = md5(sign_temp).upper()
        return signed


def md5(inp):
    """直接生成md5
    """
    if isinstance(inp, str):
        inp = inp.encode("utf-8")
    md5lib = hashlib.md5()
    md5lib.update(inp)
    return md5lib.hexdigest()
