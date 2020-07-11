# -*- coding:utf-8 -*-

import base64
from Crypto.Cipher import AES

class PKCS7Encoder(object):
    """提供基于PKCS7算法的加解密接口
    """

    def __init__(self):
        self.block_size = 32

    def encode(self, text):
        """ 对需要加密的明文进行填充补位
        @param text: 需要进行填充补位操作的明文
        @return: 补齐明文字符串
        """
        text_length = len(text)
        # 计算需要填充的位数
        amount_to_pad = self.block_size - (text_length % self.block_size)
        if amount_to_pad == 0:
            amount_to_pad = self.block_size
        # 获得补位所用的字符
        pad = chr(amount_to_pad).encode()
        return text + pad * amount_to_pad

    def decode(self, decrypted):
        """删除解密后明文的补位字符
        @param decrypted: 解密后的明文
        @return: 删除补位字符后的明文
        """
        pad = ord(decrypted[-1])
        if pad < 1 or pad > 32:
            pad = 0
        return decrypted[:-pad]


ENCRYPT_PADDING_8_BYTES = "@@@@@@@@"
ENCRYPT_PADDING_16_BYTES = "@@@@@@@@@@@@@@@@"


class DesHelper(object):
    """des加密工具类
    """
    def __init__(self, key):
        import pyDes
        if len(key) < 16:
            key = key + ENCRYPT_PADDING_8_BYTES
        key = key[0:8]
        self._des = pyDes.des(key, pyDes.CBC, key, pad=None, padmode=pyDes.PAD_PKCS5)

    def encrypt(self, plain):
        return self._des.encrypt(plain)

    def decrypt(self, cipher):
        return self._des.decrypt(cipher)

    def hex_encrypt(self, plain):
        return self._des.encrypt(plain).hex()

    def hex_decrypt(self, cipher):
        return self._des.decrypt(bytes.fromhex(cipher))


class AesHelper(object):
    def __init__(self, key):
        if len(key) < 16:
            key = key + ENCRYPT_PADDING_16_BYTES
        self._key = key[0:16]
        self._mode = AES.MODE_CBC

    def encrypt(self, text):
        """对明文进行加密
        """
        text = text.encode()
        pkcs7 = PKCS7Encoder()
        text = pkcs7.encode(text)
        try:
            cryptor = AES.new(self._key, self._mode, self._key)
            ciphertext = cryptor.encrypt(text)
            return base64.b64encode(ciphertext).decode('utf8')
        except Exception:
            return None


def des_encrypt(key, plain):
    raw_cipher = DesHelper(key).encrypt(plain)
    cipher = base64.urlsafe_b64encode(raw_cipher).decode("utf-8")
    return cipher


def des_decrypt(key, cipher):
    raw_cipher = base64.urlsafe_b64decode(cipher.encode("utf-8"))
    return DesHelper(key).decrypt(raw_cipher)
