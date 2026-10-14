# -*- coding: utf-8 -*-
"""HTTP 客户端: 维护一条 cookie 链, 每个请求都带上(与 Android 端做法一致)"""
from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple

import requests

from . import constants


def parse_cookie_text(text: str) -> List[str]:
    items = []
    for part in re.split(r";\s*", (text or "").strip()):
        if "=" in part:
            name, _, value = part.partition("=")
            if name.strip():
                items.append("%s=%s" % (name.strip(), value.strip()))
    return items


class XXTClient:
    def __init__(self, uid: str = "", fid: str = "", name: str = "",
                 cookies: str = "", timeout: Tuple[int, int] = (8, 15)):
        self.uid = uid
        self.fid = fid
        self.name = name or uid
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers["Accept-Language"] = constants.ACCEPT_LANG
        self._cookie_items: List[str] = parse_cookie_text(cookies)

    # ------------------------------------------------------------- cookie
    @property
    def cookies(self) -> str:
        return "; ".join(self._cookie_items)

    def set_cookies(self, text: str) -> None:
        self._cookie_items = parse_cookie_text(text)

    def merge_cookie(self, item: str) -> None:
        name = item.split("=", 1)[0]
        self._cookie_items = [x for x in self._cookie_items
                              if not x.startswith(name + "=")]
        self._cookie_items.append(item)

    def _apply_set_cookie(self, resp: requests.Response) -> None:
        try:
            for raw in resp.raw.headers.getlist("Set-Cookie") or []:
                first = raw.split(";", 1)[0].strip()
                if "=" in first:
                    self.merge_cookie(first)
        except Exception:
            pass

    # ------------------------------------------------------------- 请求
    def _request(self, method: str, url: str, *, ua: str = "ios",
                 referer: Optional[str] = None, params: Optional[Dict] = None,
                 data=None, headers: Optional[Dict] = None,
                 allow_redirects: bool = True) -> requests.Response:
        ua_map = {"ios": constants.UA_IOS, "ios_simple": constants.UA_IOS_SIMPLE,
                  "desktop": constants.UA_DESKTOP}
        hdrs = {
            "User-Agent": ua_map.get(ua, constants.UA_IOS),
            "Accept-Language": constants.ACCEPT_LANG,
            "Cookie": self.cookies,
        }
        if referer:
            hdrs["Referer"] = referer
        if headers:
            hdrs.update(headers)
        resp = self.session.request(method, url, headers=hdrs, params=params,
                                    data=data, timeout=self.timeout,
                                    allow_redirects=allow_redirects)
        self._apply_set_cookie(resp)
        return resp

    def get(self, url: str, ua: str = "ios", referer: Optional[str] = None,
            params: Optional[Dict] = None, headers: Optional[Dict] = None
            ) -> requests.Response:
        return self._request("GET", url, ua=ua, referer=referer, params=params,
                             headers=headers)

    def get_text(self, url: str, ua: str = "ios",
                 params: Optional[Dict] = None) -> str:
        return self.get(url, ua=ua, params=params).text

    def get_json(self, url: str, **kw) -> Optional[dict]:
        try:
            return self.get(url, **kw).json()
        except Exception:
            return None

    def post_form(self, url: str, data: Dict, ua: str = "ios",
                  referer: Optional[str] = None) -> requests.Response:
        return self._request("POST", url, ua=ua, referer=referer, data=data)

    def post_text(self, url: str, data: Dict, ua: str = "ios") -> str:
        return self.post_form(url, data, ua=ua).text

    def post_raw(self, url: str, body: str, ua: str = "ios") -> requests.Response:
        return self._request("POST", url, ua=ua, data=body,
                             headers={"Content-Type":
                                      "application/x-www-form-urlencoded; charset=utf-8"})
