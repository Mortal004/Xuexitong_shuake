# -*- coding: utf-8 -*-
"""加解密工具: AES-128-CBC(本地保存密码 / fanyalogin 传输)、MD5、设备指纹"""
from __future__ import annotations

import base64
import hashlib
import os

from .constants import AES_KEY

try:
    from Crypto.Cipher import AES
    _HAVE_CRYPTO = True
except Exception:  # pragma: no cover
    _HAVE_CRYPTO = False


def _pad(data: bytes, block: int = 16) -> bytes:
    n = block - len(data) % block
    return data + bytes([n]) * n


def _unpad(data: bytes) -> bytes:
    return data[:-data[-1]] if data else data


def aes_encrypt(text: str, key: str = AES_KEY) -> str:
    """AES/CBC/PKCS5, key==iv, Base64 无换行(与原项目一致)"""
    if not text:
        return text
    if not _HAVE_CRYPTO:
        raise RuntimeError("缺少 pycryptodome: pip install pycryptodome")
    kb = key.encode("utf-8")
    return base64.b64encode(AES.new(kb, AES.MODE_CBC, iv=kb)
                            .encrypt(_pad(text.encode("utf-8")))).decode("ascii")


def aes_decrypt(text: str, key: str = AES_KEY) -> str:
    if not text:
        return text
    if not _HAVE_CRYPTO:
        return text
    try:
        kb = key.encode("utf-8")
        return _unpad(AES.new(kb, AES.MODE_CBC, iv=kb)
                      .decrypt(base64.b64decode(text))).decode("utf-8")
    except Exception:
        return text          # 兼容明文


def md5_hex(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def generate_device_code() -> str:
    """随机设备指纹(与 Android 端 generateDeviceCode 等价: 随机 Base64)"""
    return base64.b64encode(os.urandom(32)).decode("ascii")
