"""配置读写管理器，统一管理 account_info.json 和 course_name.json 的读写"""
import json

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
        try:
            with open(self.ACCOUNT_PATH, 'r', encoding='utf-8') as f:
                self._account_info = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._account_info = {}
        return self._account_info

    def save_account(self, account_info: dict) -> bool:
        try:
            with open(self.ACCOUNT_PATH, 'w', encoding='utf-8') as f:
                json.dump(account_info, f, ensure_ascii=False, indent=2)
            return True
        except PermissionError:
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