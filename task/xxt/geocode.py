# -*- coding: utf-8 -*-
"""地址 -> 坐标 (高德地理编码)。仅当活动 content 里没有经纬度时使用。"""
from __future__ import annotations

from typing import Optional, Tuple

import requests

from . import constants, storage


def amap_key() -> str:
    return (storage.load_config().get("amap_key")
            or constants.DEFAULT_AMAP_KEY)


def geocode(address: str, timeout: int = 8) -> Tuple[Optional[float], Optional[float]]:
    """返回 (lat, lon); 失败返回 (None, None)"""
    address = (address or "").strip()
    if not address:
        return None, None
    try:
        resp = requests.get(constants.AMAP_GEOCODE_URL,
                            params={"key": amap_key(), "address": address},
                            timeout=timeout)
        data = resp.json()
        if str(data.get("status")) == "1" and data.get("geocodes"):
            lon_s, lat_s = str(data["geocodes"][0]["location"]).split(",")[:2]
            return float(lat_s), float(lon_s)
    except Exception:
        pass
    return None, None
