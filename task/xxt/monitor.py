# Copyright (c) 2025 Mortal004
# All rights reserved.
# This software is provided for non-commercial use only.
# For more information, see the LICENSE file in the root directory of this project.
# -*- coding: utf-8 -*-
"""监控循环: 拉取全部课程 -> 查找进行中的 普通/位置 签到 -> 自动签到, 每 7 秒一轮"""
from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional, Tuple

from . import constants, courses, sign, storage
from .client import XXTClient

DEFAULT_WORKERS = 5
CLIENT_FACTORY = XXTClient      # 便于测试替换


def _fetch_activities(client: XXTClient, course) -> Tuple[object, List]:
    """单个课程的活动查询(用独立会话, 保证并发安全)"""
    worker = CLIENT_FACTORY(uid=getattr(client, "uid", ""),
                            fid=getattr(client, "fid", ""),
                            name=getattr(client, "name", ""),
                            cookies=getattr(client, "cookies", ""))
    try:
        return course, courses.get_ongoing_activities(worker, course)
    except Exception as e:
        storage.log("课程 %s 活动查询异常: %s" % (course.title, e),sign_text=sign_txt)
        return course, []


def collect_ongoing(client: XXTClient, course:str) -> List:
    """并发收集所有课程里需要处理的签到活动"""
    if not course:
        return []
    results = [_fetch_activities(client, course)]

    pending = []
    for _course, acts in results:
        for act in acts:
            if not storage.is_signed(act.aid):     # 已处理过的不再提交
                pending.append(act)
    return pending
sign_txt=None


def scan_and_sign_once(client: XXTClient, course:str,sign_text=None) -> List[object]:
    """一轮检查: 返回本轮处理过的活动列表"""
    global sign_txt
    sign_txt=sign_text
    handled = []
    pending = collect_ongoing(client, course)
    if pending:
        storage.log("本轮发现 %d 个待处理签到" % len(pending),sign_text=sign_txt)
    for act in pending:
        try:
            result = sign.sign_activity(client, act,sign_text=sign_txt)
        except Exception as e:
            storage.log("  签到异常 %s: %s" % (act.aid, e),sign_text=sign_txt)
            continue
        storage.log("  结果: %s" % result.text,sign_text=sign_txt)
        if result.is_ok() or result.locked or result.auth_error \
                or result.need_captcha or result.need_face or result.need_photo:
            if result.need_captcha or result.need_face or result.need_photo:
                storage.log("  该签到需要额外验证(滑块/人脸/拍照), 本次跳过",sign_text=sign_txt)
            storage.mark_signed(act.aid, result.text, act.name, act.course.title)
            handled.append(act)
    return handled

