# Copyright (c) 2025 Mortal004
# All rights reserved.
# This software is provided for non-commercial use only.
# For more information, see the LICENSE file in the root directory of this project.
"""配置读写管理器，统一管理 account_info.json 和 course_name.json 的读写"""
import json
import os
import time

class ConfigManager:
    ACCOUNT_PATH = r'task/tool/account_info.json'
    COURSE_PATH = r'task/tool/course_name.json'
    VERSION_PATH = r'task/tool/version_info'
    HELP_PATH = r'task/tool/Help.txt'
    COURSE_PROCESS_PATH = r'task/tool/course_process.json'

    def __init__(self):
        self._account_info = {}

    # ========== 账户信息 ==========
    def load_account(self) -> dict:
        # 多端模式下 GUI 会不断重写 account_info.json，子进程可能读到写了一半的文件；
        # 这里重试几次，避免因为偶发的 JSONDecodeError 把邮箱配置当成"未开启"。
        for attempt in range(4):
            try:
                with open(self.ACCOUNT_PATH, 'r', encoding='utf-8') as f:
                    self._account_info = json.load(f)
                return self._account_info
            except FileNotFoundError:
                self._account_info = {}
                return self._account_info
            except json.JSONDecodeError:
                if attempt < 3:
                    time.sleep(0.08)
        self._account_info = {}
        return self._account_info

    @staticmethod
    def _atomic_write(path, data):
        """先写临时文件再替换，避免其它进程读到半个 JSON"""
        tmp = f'{path}.{os.getpid()}.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)

    def save_account(self, account_info: dict) -> bool:
        try:
            self._atomic_write(self.ACCOUNT_PATH, account_info)
            return True
        except (PermissionError, OSError):
            return False

    def get_account(self) -> dict:
        return self._account_info

    # ========== 课程数据 ==========
    def load_courses(self, phone_number: str) -> list:
        try:
            with open(self.COURSE_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}
        return data.get(phone_number, [])

    def save_courses(self, phone_number: str, courses: list):
        try:
            with open(self.COURSE_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}
        existing = data.get(phone_number, [])
        data[phone_number] = list(set(existing + courses))
        with open(self.COURSE_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # ========== 邮箱通知 ==========
    EMAIL_FIELDS = {
        'enabled': 'email_notify',
        'provider': 'email_provider',
        'account': 'email_account',
        'auth_code': 'email_auth_code',
        'receiver': 'email_receiver',
        'host': 'email_smtp_host',
        'port': 'email_smtp_port',
        'use_ssl': 'email_use_ssl',
    }

    def get_email_config(self) -> dict:
        """读取邮箱通知配置（auth_code 为落盘原值，由 mailer 负责解码）"""
        account = self.load_account()

        def _int(key, default=0):
            try:
                return int(account.get(key, default) or 0)
            except (TypeError, ValueError):
                return default

        return {
            'enabled': _int('email_notify', 0),
            'provider': account.get('email_provider') or 'QQ邮箱',
            'account': account.get('email_account') or '',
            'auth_code': account.get('email_auth_code') or '',
            'receiver': account.get('email_receiver') or '',
            'host': account.get('email_smtp_host') or '',
            'port': _int('email_smtp_port', 0),
            'use_ssl': _int('email_use_ssl', 1),
        }

    def save_email_config(self, **kwargs) -> bool:
        """只更新邮箱相关字段，不动其它配置"""
        data = {}
        for attempt in range(3):
            try:
                with open(self.ACCOUNT_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                break
            except FileNotFoundError:
                data = {}
                break
            except json.JSONDecodeError:
                if attempt < 2:
                    time.sleep(0.08)
        for key, value in kwargs.items():
            field = self.EMAIL_FIELDS.get(key)
            if field:
                data[field] = value
        try:
            self._atomic_write(self.ACCOUNT_PATH, data)
        except (PermissionError, OSError):
            return False
        self._account_info = data
        return True

    # ========== 便捷方法 ==========
    def get_version(self) -> str:
        try:
            with open(self.VERSION_PATH, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            return '0.0.0'

    def get_help_text(self) -> str:
        try:
            with open(self.HELP_PATH, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return '帮助文档未找到'
    def get_course_process(self) -> dict:
        try:
            with open(self.COURSE_PROCESS_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)

        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def count_video_records(self) -> int:
        import os
        record_dir = 'task/record'
        if not os.path.isdir(record_dir):
            return 0
        total = 0
        for fname in os.listdir(record_dir):
            if '刷课记录' in fname and fname.endswith('.txt'):
                try:
                    with open(os.path.join(record_dir, fname), 'r', encoding='utf-8') as f:
                        total += f.read().count('视频')
                except Exception:
                    pass
        return total

    def get_popup_count(self) -> int:
        account = self.load_account()
        return account.get('popup_count', 0)

    def increment_popup_count(self, video_count: int):
        account = self.load_account()
        account['popup_count'] = video_count
        self.save_account(account)