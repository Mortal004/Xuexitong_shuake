# -*- coding: utf-8 -*-
"""
本地存储 (data/ 目录)

config.json  登录信息: 手机号 + 加密密码 + Cookie + uid/fid + 真实姓名 + 登录时间
              —— 下次启动直接复用, 无需再输账号密码
signed.json  已处理过的活动(避免每 7 秒重复提交)
sign.log     签到/运行日志(纯文本, 追加)
"""
from __future__ import annotations

import json
import os
import threading
import time
from typing import Any, Dict, Optional

from .crypto import aes_decrypt, aes_encrypt

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

CONFIG_FILE = "config.json"
SIGNED_FILE = "signed.json"
COORD_FILE = "coords.json"
LOG_FILE = "sign.log"

_lock = threading.RLock()


def _path(name: str) -> str:
    os.makedirs(DATA_DIR, exist_ok=True)
    return os.path.join(DATA_DIR, name)


def _read_json(name: str, default: Any) -> Any:
    try:
        with open(_path(name), "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _write_json(name: str, data: Any) -> None:
    with _lock:
        tmp = _path(name) + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, _path(name))


# ---------------------------------------------------------------------------
# 登录信息
# ---------------------------------------------------------------------------
def load_config() -> Dict[str, Any]:
    return _read_json(CONFIG_FILE, {}) or {}


def save_config(username: str, password: str, uid: str, fid: str,
                cookies: str, real_name: str = "") -> Dict[str, Any]:
    """保存登录信息(密码 AES 加密), 供下次免输入登录"""
    cfg = {
        "username": username,
        "password": aes_encrypt(password) if password else "",
        "uid": str(uid),
        "fid": str(fid),
        "cookies": cookies,
        "real_name": real_name or "",
        "login_ts": int(time.time() * 1000),
    }
    _write_json(CONFIG_FILE, cfg)
    return cfg


def update_config(**kwargs) -> Dict[str, Any]:
    cfg = load_config()
    for k, v in kwargs.items():
        if k == "password" and v:
            cfg["password"] = aes_encrypt(v)
        else:
            cfg[k] = v
    cfg["login_ts"] = int(time.time() * 1000)
    _write_json(CONFIG_FILE, cfg)
    return cfg


def config_password(cfg: Optional[Dict[str, Any]] = None) -> str:
    cfg = cfg or load_config()
    return aes_decrypt(cfg.get("password", "") or "")


def clear_config() -> None:
    try:
        os.remove(_path(CONFIG_FILE))
    except Exception:
        pass


# ---------------------------------------------------------------------------
# 已处理活动
# ---------------------------------------------------------------------------
def load_signed() -> Dict[str, Any]:
    return _read_json(SIGNED_FILE, {}) or {}


def mark_signed(aid: str, status: str, title: str = "", course: str = "") -> None:
    data = load_signed()
    data[str(aid)] = {
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "status": status,
        "title": title,
        "course": course,
    }
    # 控制体积: 只保留最近 500 条
    if len(data) > 500:
        items = sorted(data.items(), key=lambda kv: kv[1].get("time", ""))
        data = dict(items[-500:])
    _write_json(SIGNED_FILE, data)


def is_signed(aid: str) -> bool:
    return str(aid) in load_signed()


# ---------------------------------------------------------------------------
# 定位坐标缓存: 按"教师地址"记住上次签到成功的位置, 下次直接从这里开始试
# ---------------------------------------------------------------------------
def _addr_key(address: str) -> str:
    import hashlib
    return hashlib.md5((address or "").strip().encode("utf-8")).hexdigest()[:16]


def load_cached_coord(address: str) -> Optional[Dict[str, Any]]:
    if not address:
        return None
    return (load_coord_cache() or {}).get(_addr_key(address))


def load_coord_cache() -> Dict[str, Any]:
    return _read_json(COORD_FILE, {}) or {}


def save_cached_coord(address: str, lat, lon) -> None:
    if not address:
        return
    data = load_coord_cache()
    data[_addr_key(address)] = {
        "lat": float(lat), "lon": float(lon),
        "address": address[:80],
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    if len(data) > 200:
        items = sorted(data.items(), key=lambda kv: kv[1].get("time", ""))
        data = dict(items[-200:])
    _write_json(COORD_FILE, data)


# ---------------------------------------------------------------------------
# 日志
# ---------------------------------------------------------------------------
import tkinter as tk

def _safe_insert(sign_text, line):
    sign_text.insert(tk.END, line + "\n")
    sign_text.see(tk.END)

def log(message: str, sign_text=None) -> None:
    line = message.strip()
    if sign_text is not None:
        sign_text.after(0, _safe_insert, sign_text, line)
    try:
        with _lock:
            with open(_path(LOG_FILE), "a", encoding="utf-8") as f:
                f.write(line + "\n")
    except Exception:
        pass