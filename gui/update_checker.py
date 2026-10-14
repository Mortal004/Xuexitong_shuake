"""更新检查与网盘选择弹窗"""
import random
import re
import tkinter as tk
import customtkinter as ctk
import requests
import logging
from datetime import datetime

def parse_date(s: str):
    parts = s.split(".")
    if len(parts) != 3:
        raise ValueError("格式应为 年.月.日")

    y, m, d = map(int, parts)

    # 两位年份补全：00-69 -> 2000-2069，70-99 -> 1970-1999
    if y < 100:
        y += 2000 if y < 70 else 1900

    return datetime(y, m, d).date()

logger = logging.getLogger(__name__)

class UpdateChecker:
    RELEASE_URL = 'https://api.github.com/repos/Mortal004/Xuexitong_shuake/releases/latest'

    def __init__(self, root, get_version, get_colors):
        self.root = root
        self.get_version = get_version
        self.get_colors = get_colors
        self.updata_concent = ""

    def check(self):
        text = ''
        try:
            headers = {"User-Agent": random.choice([
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/58.0.3029.110 Safari/537.3",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/58.0.3029.81 Safari/537.3",
                "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
            ])}
            response = requests.get(self.RELEASE_URL, headers=headers, timeout=10)
            if response.status_code == 200:
                release_info = response.json()
                self.updata_concent = release_info.get('body', '')
                assets = release_info.get('assets', [])
                if assets:
                    file_name = assets[0].get('name', '')
                    version = self.get_version()
                    announce = self._show_selection(version, file_name)
                    if version in file_name:
                        text=f'\n当前版本为最新版本，无需更新！'
                        logger.info(f'版本{version}已是最新')
                    else:
                        text=f'\n检测到有新版本可用'
                        logger.info(f'版本{version}需要更新到{file_name}')

                    text+=f'\n{announce}'
            else:
                text = '\n检查更新失败，请检查网络连接！'
        except Exception as e:
            text='\n检查更新失败，请检查网络连接！'
            logger.error(f'检查更新失败：{e}')
        return text

    def _parse_update_content(self):
        """解析更新内容，分离公告、更新说明和网盘链接"""
        text = self.updata_concent or ''
        urls = {}

        # ---- 1. 提取三个网盘链接 ----
        for drive_name in ['迅雷网盘', '夸克网盘', '百度网盘']:
            match = re.search(
                rf'{drive_name}[：:]\s*[`\'"]?(https?://[^\s`\'"，,，]+)',
                text
            )
            if match:
                urls[drive_name] = match.group(1).rstrip('#')

        # ---- 2. 提取公告 ----
        announcement = ''
        ann_match = re.search(
            r'公告[：:]\s*(.*?)(?=更新内容[：:]|下载链接[：:]|$)',
            text,
            re.DOTALL
        )
        if ann_match:
            announcement = ann_match.group(0).strip()
            # 公告超过 22 个字，每 22 字加换行
            announcement = self._wrap_text(announcement, 27)

        # ---- 3. 提取更新内容 ----
        update_content = ''
        upd_match = re.search(
            r'更新内容[：:]\s*(.*?)(?=下载链接[：:]|$)',
            text,
            re.DOTALL
        )
        if upd_match:
            update_content = upd_match.group(1).strip()

        # ---- 4. 清理多余空行 ----
        announcement = re.sub(r'\n{3,}', '\n\n', announcement).strip()
        update_content = re.sub(r'\n{3,}', '\n\n', update_content).strip()

        return announcement, update_content, urls

    @staticmethod
    def _char_unit(ch):
        """单个字符占用的字数单位：中文 1，英文/数字 0.5，其他标点 1"""
        if ch.isdigit():
            return 0.5
        if 'a' <= ch <= 'z' or 'A' <= ch <= 'Z':
            return 0.5
        return 1

    @staticmethod
    def _wrap_text(text, width=22):
        """
        按字宽单位换行：
          中文/标点 = 1 个单位，英文/数字 = 0.5 个单位
          当累计单位超过 width 时插入换行符
        """

        def unit(ch):
            if ch.isdigit():
                return 0.5
            if 'a' <= ch <= 'z' or 'A' <= ch <= 'Z':
                return 0.5
            return 1

        lines = text.split('\n')
        new_lines = []
        for line in lines:
            if not line:
                new_lines.append(line)
                continue

            cur = ''
            cur_unit = 0.0
            for ch in line:
                u = unit(ch)
                # 加上这个字符会超过 width，则先换行
                if cur and cur_unit + u > width:
                    new_lines.append(cur)
                    cur = ch
                    cur_unit = u
                else:
                    cur += ch
                    cur_unit += u
            if cur:
                new_lines.append(cur)

        return '\n'.join(new_lines)

    def _show_selection(self, version, file_name):
        colors = self.get_colors()
        win = ctk.CTkToplevel(self.root)
        win.iconbitmap(r'task\img\xuexitong1 .ico')
        win.title("发现新版本")
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()
        win.attributes("-topmost", True)
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (500 // 2)
        y = (win.winfo_screenheight() // 2) - (420 // 2)
        win.geometry(f"+{x}+{y}")


        main_frame = ctk.CTkFrame(win, corner_radius=20)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 标题
        title_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        title_frame.pack(pady=(10, 5))
        ctk.CTkLabel(title_frame, text="✨", font=("Segoe UI Emoji", 32)).pack(side="left", padx=5)
        ctk.CTkLabel(title_frame, text="新版本可用", font=("Helvetica", 20, "bold")).pack(side="left", padx=5)

        # 更新内容
        announcement, update_content, drive_urls = self._parse_update_content()

        update_container = ctk.CTkFrame(main_frame, corner_radius=12, fg_color="#f0f0f0", height=10)
        update_container.pack(pady=(5, 10), padx=10, fill="x")
        ctk.CTkLabel(ctk.CTkFrame(update_container, fg_color="transparent"),
                     text="📦", font=("Segoe UI Emoji", 14)).pack(side="left", padx=12, pady=(8, 0))
        content_label = ctk.CTkTextbox(update_container, height=110, width=197, fg_color='transparent')
        content_label.insert(tk.END, update_content)
        content_label.pack(fill="x", padx=5, pady=2)

        # 网盘按钮
        self._build_drive_buttons(main_frame, win, colors, drive_urls)

        # 底部
        ctk.CTkFrame(main_frame, height=2, fg_color="gray70").pack(fill="x", pady=(10, 10), padx=30)
        bottom_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        bottom_frame.pack(pady=(0, 10))
        ctk.CTkButton(bottom_frame, text="跳过此次更新", font=("Helvetica", 12),
                      fg_color="transparent", hover_color="#E0E0E0", text_color="gray",
                      border_width=2, border_color="gray", corner_radius=8,
                      width=140, height=32, command=win.destroy).pack(side="left", padx=10)
        ctk.CTkLabel(bottom_frame, text="后续可在「主页」中再次检查更新",
                     font=("Helvetica", 10), text_color="gray").pack(side="right", padx=10)

        win.bind('<Return>', lambda e: self._open_drive(
            "https://pan.xunlei.com/s/VOvtzs6dbiSGyNE41Fk5ytgVA1?pwd=tct2#", win))
        win.bind('<Escape>', lambda e: win.destroy())
        if version in file_name:
            win.destroy()  # 关键：立刻隐藏
        return announcement

    def _build_drive_buttons(self, parent, window, colors, drive_urls=None):
        if drive_urls is None:
            drive_urls = {}
        drive_container = ctk.CTkFrame(parent, corner_radius=12, fg_color="#f0f0f0")
        drive_container.pack(pady=(0, 10), padx=10, fill="x")
        ctk.CTkLabel(ctk.CTkFrame(drive_container, fg_color="transparent"),
                     text="☁️ 选择下载方式", font=("Helvetica", 13, "bold"),
                     text_color="#333333").pack(anchor="w", padx=12, pady=(8, 5))
        ctk.CTkLabel(drive_container, text="建议使用推荐渠道以获得更快的速度",
                     font=("Helvetica", 11), text_color="#666666").pack(pady=(0, 8), padx=10)

        cloud_drives = [
            ("⚡ 迅雷网盘", "推荐 · 支持迅雷加速下载", "#00A8FF", "#33B9FF",
             drive_urls.get('迅雷网盘', 'https://pan.xunlei.com/s/VOvtzs6dbiSGyNE41Fk5ytgVA1?pwd=tct2#')),
            ("☁️ 夸克网盘", " 下载速度快", "#FF6B35", "#FF8555",
             drive_urls.get('夸克网盘', 'https://pan.quark.cn/s/bbcc17bcce22')),
            ("🐻 百度网盘", "提取码: 无", "#4CD964", "#6DE07E",
             drive_urls.get('百度网盘', 'https://pan.baidu.com/s/5TvAVKIajPhOKTGd9qWDfUw')),
        ]
        buttons_frame = ctk.CTkFrame(drive_container, fg_color="transparent")
        buttons_frame.pack(pady=(0, 12), padx=10, fill="x")
        for name, desc, clr, hvr, url in cloud_drives:
            btn = ctk.CTkButton(buttons_frame, text=f"{name}\n{desc}",
                                font=("Helvetica", 13, "bold"), fg_color=clr,
                                hover_color=hvr, text_color="white",
                                corner_radius=12, height=70)
            btn.pack(pady=6, fill="x")
            btn.configure(command=lambda u=url: self._open_drive(u, window))

    def _open_drive(self, url, window=None):
        import webbrowser
        webbrowser.open(url)
        tk.messagebox.showinfo("成功", "已打开浏览器访问网盘链接\n链接已复制到剪贴板")
        self.root.clipboard_clear()
        self.root.clipboard_append(url)
        if window:
            window.destroy()