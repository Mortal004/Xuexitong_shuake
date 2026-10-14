# -*- coding: utf-8 -*-
"""课程列表 + 进行中签到活动扫描"""
from __future__ import annotations

from typing import Dict, List, Optional

from . import constants
from .client import XXTClient


class Course:
    def __init__(self, course_id, class_id, course_name="", class_name="",
                 teacher="", cpi=""):
        self.course_id = str(course_id)
        self.class_id = str(class_id)
        self.course_name = course_name or ""
        self.class_name = class_name or ""
        self.teacher = teacher or ""
        self.cpi = str(cpi or "")

    @property
    def title(self) -> str:
        bits = [self.course_name or self.class_name or "未知课程"]
        if self.class_name and self.class_name != self.course_name:
            bits.append(self.class_name)
        if self.teacher:
            bits.append(self.teacher)
        return " / ".join(bits)

    def __repr__(self):  # pragma: no cover
        return "<Course %s %s>" % (self.course_id, self.title)


class Activity:
    def __init__(self, aid, name, other_id, status, course: Course,
                 start_time: int = 0):
        self.aid = str(aid)
        self.name = name or "签到"
        self.other_id = str(other_id or "")
        self.status = str(status or "")
        self.course = course
        self.start_time = int(start_time or 0)

    @property
    def sign_type_text(self) -> str:
        return {"0": "普通签到", "4": "位置签到"}.get(self.other_id,
                                                     "类型%s" % self.other_id)

    def __repr__(self):  # pragma: no cover
        return "<Activity %s %s %s>" % (self.aid, self.sign_type_text, self.status)


def get_courses(client: XXTClient) -> List[Course]:
    """获取全部课程"""
    data = client.get_json(constants.COURSE_LIST, ua="ios")
    if not isinstance(data, dict) or data.get("result") != 1:
        return []
    courses: List[Course] = []
    for item in data.get("channelList") or []:
        content = item.get("content") or {}
        course_data = ((content.get("course") or {}).get("data")) or []
        if not course_data:
            continue
        first = course_data[0] if isinstance(course_data, list) else {}
        class_id = item.get("key") or content.get("id")
        if class_id is None or not first.get("id"):
            continue
        courses.append(Course(
            course_id=first.get("id"),
            class_id=class_id,
            course_name=first.get("name") or "",
            class_name=content.get("name") or "",
            teacher=first.get("teacherfactor") or "",
            cpi=content.get("cpi") or item.get("cpi") or "",
        ))
    return courses


def _unwrap(root: Dict) -> Dict:
    """v2 接口把 activeList 放在 data 里"""
    if isinstance(root, dict) and isinstance(root.get("data"), dict) \
            and "activeList" in root["data"]:
        return root["data"]
    return root if isinstance(root, dict) else {}


def get_ongoing_activities(client: XXTClient, course: Course) -> List[Activity]:
    """课程内进行中的“普通/位置”签到活动"""
    root = client.get_json(
        "%s?fid=0&courseId=%s&classId=%s" % (constants.ACTIVE_LIST,
                                             course.course_id, course.class_id),
        ua="ios")
    data = _unwrap(root or {})
    acts: List[Activity] = []
    for entry in (data.get("activeList") or []):
        if not isinstance(entry, dict):
            continue
        if entry.get("id") is None:
            continue
        if str(entry.get("status")) != "1":          # 1 = 进行中
            continue
        if str(entry.get("activeType") or "2") != "2":  # 2 = 签到类活动
            continue
        other_id = str(entry.get("otherId") or "")
        if other_id not in (constants.SIGN_NORMAL, constants.SIGN_LOCATION):
            continue                                  # 只处理普通/位置签到
        acts.append(Activity(
            aid=entry.get("id"),
            name=entry.get("nameOne") or "签到",
            other_id=other_id,
            status=entry.get("status"),
            start_time=entry.get("startTime") or 0,
            course=course,
        ))
    return acts
