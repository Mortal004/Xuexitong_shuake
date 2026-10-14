# -*- coding: utf-8 -*-
"""
登录: 仅支持"手机号 + 密码"

流程:
  1) 优先 fanyalogin (凭证 AES 加密后 POST)
  2) 失败回退 v11/loginregister (GET, 与原 App 一致)
  3) 成功后把 Cookie/uid/fid/手机号/加密密码写入 data/config.json
     —— 下次启动直接复用, 不需要再输入账号密码
  4) Cookie 失效时用保存的密码自动重登(5 天后也会主动续期)
"""
from __future__ import annotations

import time
from typing import Optional, Tuple
from urllib.parse import quote

from . import constants, storage
from .client import XXTClient
from .crypto import aes_encrypt


class LoginError(Exception):
    pass


def _json(text: str):
    import json
    try:
        return json.loads((text or "").strip())
    except Exception:
        return None


def _cookie_value(client: XXTClient, name: str) -> str:
    for item in reversed(client._cookie_items):
        k, _, v = item.partition("=")
        if k == name:
            return v
    return ""


def login_by_password(client: XXTClient, phone: str, password: str
                      ) -> Tuple[bool, str, str, str]:
    """返回 (是否成功, 消息, uid, fid)"""
    # 1) fanyalogin
    body = ("fid=-1&uname=" + quote(aes_encrypt(phone), safe="")
            + "&password=" + quote(aes_encrypt(password), safe="")
            + "&refer=https%3A%2F%2Fi.chaoxing.com&t=true&forbidotherlogin=0"
              "&validate=&doubleFactorLogin=0&independentId=0&independentNameId=0")
    try:
        text = client.post_raw(constants.FANYALOGIN_URL, body).text
        data = _json(text)
        if data and (data.get("status") is True
                     or str(data.get("status")).lower() == "true"):
            uid = _cookie_value(client, "UID") or _cookie_value(client, "_uid")
            fid = _cookie_value(client, "fid")
            return True, "登录成功", uid, fid
        msg = (data or {}).get("msg2") or (data or {}).get("msg") or "登录失败"
        if "验证码" in str(msg):
            return False, "账号被要求行为验证(%s), 请稍后重试或在 App 登录一次" % msg, "", ""
    except Exception:
        pass

    # 2) 回退: v11/loginregister
    try:
        url = ("%s?code=%s&cx_xxt_passport=json&uname=%s&loginType=1&roleSelect=true"
               % (constants.LOGIN_REGISTER, password, quote(phone, safe="")))
        resp = client.get(url, ua="desktop", referer=constants.REFERER_MOOC,
                          headers={"Accept": "text/html,application/xhtml+xml,"
                                             "application/xml;q=0.9,*/*;q=0.8"})
        data = _json(resp.text)
        if data and (data.get("status") is True
                     or str(data.get("status")).lower() == "true"):
            uid = _cookie_value(client, "UID") or _cookie_value(client, "_uid")
            fid = _cookie_value(client, "fid")
            return True, "登录成功", uid, fid
        msg = (data or {}).get("msg2") or (data or {}).get("msg") or "账号或密码错误"
        return False, str(msg), "", ""
    except Exception as e:
        return False, "网络异常: %s" % e, "", ""


def fetch_real_name(client: XXTClient) -> str:
    """取真实姓名(签到 name 参数用), 失败则退回手机号"""
    try:
        resp = client.get(constants.GET_PUID, ua="ios_simple")
        data = _json(resp.text)
        if isinstance(data, dict):
            msg = data.get("msg")
            if isinstance(msg, dict) and msg.get("name"):
                return str(msg["name"])
            if isinstance(msg, str):
                inner = _json(msg)
                if isinstance(inner, dict) and inner.get("name"):
                    return str(inner["name"])
    except Exception:
        pass
    return ""


def do_login(phone: str, password: str) -> Tuple[Optional[XXTClient], str]:
    """登录并保存登录信息; 返回 (client, 消息)"""
    client = XXTClient()
    ok, msg, uid, fid = login_by_password(client, phone, password)
    if not ok:
        return None, msg
    name = fetch_real_name(client) or phone
    client.uid, client.fid, client.name = uid, fid, name
    storage.save_config(phone, password, uid, fid, client.cookies, name)
    return client, "登录成功: %s (uid=%s)" % (name, uid)


def restore_client(sign_text) -> Optional[XXTClient]:
    """用本地保存的信息恢复会话; Cookie 失效时自动用保存的密码重登"""
    cfg = storage.load_config()
    if not cfg:
        return None

    client = XXTClient(uid=cfg.get("uid", ""), fid=cfg.get("fid", ""),
                       name=cfg.get("real_name") or cfg.get("username", ""),
                       cookies=cfg.get("cookies", ""))

    if cfg.get("cookies") and check_login(client):
        client.name = cfg.get("real_name") or cfg.get("username") or client.name
        # 超过 5 天主动续期, 避免 Cookie 过期
        ts = cfg.get("login_ts") or 0
        if time.time() * 1000 - ts > 5 * 24 * 60 * 60 * 1000:
            password = storage.config_password(cfg)
            if password:
                ok, msg, uid, fid = login_by_password(client, cfg.get("username", ""), password)
                if ok:
                    client.uid, client.fid = uid, fid
                    storage.update_config(uid=uid, fid=fid, cookies=client.cookies)
                    storage.log("Cookie 已自动续期",sign_text=sign_text)
        return client

    # Cookie 失效 -> 用保存的密码自动重登
    phone = cfg.get("username") or ""
    password = storage.config_password(cfg)
    if phone and password:
        storage.log("Cookie 已失效, 正在用保存的账号密码自动重新登录...",sign_text=sign_text)
        ok, msg, uid, fid = login_by_password(client, phone, password)
        if ok:
            name = fetch_real_name(client) or phone
            client.uid, client.fid, client.name = uid, fid, name
            storage.update_config(uid=uid, fid=fid, cookies=client.cookies,
                                  real_name=name)
            storage.log("自动重新登录成功: %s" % name,sign_text=sign_text)
            return client
        storage.log("自动重新登录失败: %s" % msg,sign_text=sign_text)
    return None


def check_login(client: XXTClient) -> bool:
    """用课程列表接口验证登录态"""
    try:
        data = client.get_json(constants.COURSE_LIST, ua="ios")
        return bool(isinstance(data, dict) and data.get("result") == 1)
    except Exception:
        return False
