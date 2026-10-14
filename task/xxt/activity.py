# -*- coding: utf-8 -*-
"""
活动详情获取与解析

多个来源合并(任一来源可能带定位坐标):
  1) getPPTActiveInfo?activeId=X
  2) getPPTActiveInfo?activeId=X&duid=&denc=
  3) newsign/signDetail?activePrimaryId=X&type=1
位置签到的坐标/地址都从这里取(content.locationLatitude / locationLongitude /
locationLatitude_gd / locationLongitude_gd / locationText)。
"""
from __future__ import annotations

import json
from typing import Dict, List, Optional, Tuple

from . import constants
from .client import XXTClient


def _nested_data(resp) -> Optional[dict]:
    if not isinstance(resp, dict):
        return None
    data = resp.get("data")
    if isinstance(data, str):
        try:
            return json.loads(data)
        except Exception:
            return None
    return data if isinstance(data, dict) else None


def _content_of(data: Dict) -> Dict:
    content = data.get("content")
    if isinstance(content, str):
        try:
            content = json.loads(content)
        except Exception:
            content = None
    return content if isinstance(content, dict) else {}


def _merge(target: Dict, source: Dict) -> None:
    tc, sc = _content_of(target), _content_of(source)
    for k, v in sc.items():
        if v not in (None, "", "0") and tc.get(k) in (None, ""):
            tc[k] = v
    for k in ("locationText", "locationLatitude", "locationLongitude",
              "locationLatitude_gd", "locationLongitude_gd"):
        if source.get(k) and not target.get(k):
            target[k] = source[k]
        if target.get(k) and not tc.get(k):
            tc[k] = target[k]
    if tc:
        target["content"] = json.dumps(tc, ensure_ascii=False)
    for k, v in source.items():
        if k == "content":
            continue
        if target.get(k) in (None, "", "0") and v not in (None, ""):
            target[k] = v


def fetch_activity_info(client: XXTClient, aid: str) -> Dict:
    """获取并合并活动详情"""
    merged: Dict = {}
    for url in ("%s?activeId=%s" % (constants.ACTIVE_INFO, aid),
                "%s?activeId=%s&duid=&denc=" % (constants.ACTIVE_INFO, aid)):
        data = _nested_data(client.get_json(url, ua="ios"))
        if data:
            _merge(merged, data)
    if not merged.get("content") or not merged.get("otherId"):
        detail = client.get_json(
            "%s?activePrimaryId=%s&type=1" % (constants.SIGN_DETAIL, aid), ua="ios")
        if isinstance(detail, dict) and detail:
            _merge(merged, detail)
    return merged


def activity_content(client: XXTClient, aid: str,
                     cached: Optional[Dict] = None) -> Dict:
    data = cached if cached else fetch_activity_info(client, aid)
    return _content_of(data)


def _float_or_none(value) -> Optional[float]:
    try:
        text = str(value).strip() if value is not None else ""
        return float(text) if text else None
    except Exception:
        return None


def coordinate_candidates(content: Dict) -> List[Tuple[float, float, str]]:
    """
    从 content 中收集候选坐标(按准确度排序):
      1) locationLatitude + locationLongitude       服务器判定基准(BD09), 优先
      2) locationLatitude + locationLongitude_gd    原 Android 代码使用的混合对
      3) locationLatitude_gd + locationLongitude_gd 高德 GCJ02 对
      4) latitude + longitude
    """
    cands: List[Tuple[float, float, str]] = []

    def add(lat, lon, label):
        if lat is None or lon is None or (lat == 0 and lon == 0):
            return
        for la, lo, _ in cands:
            if abs(la - lat) < 1e-9 and abs(lo - lon) < 1e-9:
                return
        cands.append((lat, lon, label))

    add(_float_or_none(content.get("locationLatitude")),
        _float_or_none(content.get("locationLongitude")), "content(百度BD09对)")
    add(_float_or_none(content.get("locationLatitude")),
        _float_or_none(content.get("locationLongitude_gd")), "content(混合对)")
    add(_float_or_none(content.get("locationLatitude_gd")),
        _float_or_none(content.get("locationLongitude_gd")), "content(高德GCJ02对)")
    add(_float_or_none(content.get("latitude")),
        _float_or_none(content.get("longitude")), "content(latitude/longitude)")
    return cands


def content_address(content: Dict) -> str:
    return str(content.get("locationText") or "").strip()
