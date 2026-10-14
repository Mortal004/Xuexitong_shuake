# Copyright (c) 2025 Mortal004
# All rights reserved.
# This software is provided for non-commercial use only.
# For more information, see the LICENSE file in the root directory of this project.
#激活环境start_venv\Scripts\activate
#打包python -m PyInstaller --onefile --noconsole start.py
#python -m PyInstaller --onefile --noconsole --icon=xuexitong.ico start.py
import json
import signal
import time
from datetime import datetime, timedelta
import re
import threading
import tkinter as tk
import subprocess
from PIL import Image
from colorama import Fore
from tkinter import ttk, messagebox
import os
import customtkinter as ctk
import pickle
import logging

from gui.sponsor_panel import SponsorPanel
from core.config_manager import ConfigManager
from gui.user_notice import UserNotice
from gui.update_checker import UpdateChecker
from gui.timer_window import TimerWindow
from gui.setting_panel import SettingsPanel
from gui.sign_window import SignWindow

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("输出记录.log", encoding='utf-8')]
)
logger = logging.getLogger(__name__)

class Start:
    def __init__(self):
        self.announcement =("注意：该脚本不可用作商用、引流,使用该脚本产生的任何后果由使用者"
                                                 "自行承担,开发者不承担任何责任; 没有QQ群，谨防上当受骗")
        self.lab_lst = []
        self.thread = None
        self.config = ConfigManager()
        self.timer_active = False

        self.dynamic_rows = []
        self.process = {}
        self.text_box_lst=[]

        self.colorama_to_tkinter = {
            'RED': 'red',
            'YELLOW': 'yellow',
            'BLUE': 'blue',
            'GREEN': 'green',
            'MAGENTA': 'magenta'
        }
        self.color_value_dict = {
            '海洋蓝': ['#1E88E5', '#E3F2FD', '#81AED1'],
            '清新绿': ['#2E7D32', '#E8F5E9', '#A5D6A7'],
            '暖阳橙': ['#F57C00', '#FFF3E0', '#FFB74D'],
            '淡雅灰': ['#607D8B', '#ECEFF1', '#B0BEC5'],
            '天空湖': ['#00838F', '#E0F7FA', '#80DEEA'],
            '深邃夜': ['#2C3E50', '#ECF0F1', '#BDC3C7'],
            '紫罗兰': ['#6A1B9A', '#F3E5F5', '#CE93D8']}
        self.font = ("Helvetica", 13)
        self.record_color_lst = ['海洋蓝']

        self.frame_fg_color = self.color_value_dict[self.record_color_lst[0]][1]
        self.button_color = self.color_value_dict[self.record_color_lst[0]][0]
        self.button_hover_color = self.color_value_dict[self.record_color_lst[0]][2]
        self.root = ctk.CTk()
        ctk.set_appearance_mode("light")
        self.root.geometry("+1050+20")
        with open(r'task/tool/version_info', 'r', encoding='utf-8') as f:
            version_info = f.read()
            self.root.title(f'学习通刷课 {version_info}')
        self.main_frame = ctk.CTkFrame(self.root, fg_color=self.frame_fg_color, corner_radius=0)
        self.set_frame = ctk.CTkFrame(self.root, fg_color=self.frame_fg_color, corner_radius=0)
        self.help_frame = ctk.CTkFrame(self.root, fg_color=self.frame_fg_color, corner_radius=0)
        self.vido_frame = ctk.CTkFrame(self.root, fg_color=self.frame_fg_color, corner_radius=0)
        self.score_frame = ctk.CTkFrame(self.root, fg_color=self.frame_fg_color, corner_radius=0)
        self.question_bank_frame = ctk.CTkFrame(self.root, fg_color=self.frame_fg_color, corner_radius=0)
        self.error_frame = ctk.CTkFrame(self.root, fg_color=self.frame_fg_color, corner_radius=0)
        self.money_frame = ctk.CTkFrame(self.root, fg_color=self.frame_fg_color, corner_radius=0)
        self.root.resizable(False, False)
        self.root.iconbitmap(r'task\img\xuexitong1 .ico')
        self.root.attributes('-alpha', 1)
        # 初始化子模块
        self._updater = UpdateChecker(self.root, self.config.get_version, self._get_colors)
        self._timer = TimerWindow(self.root, self._on_timer_set, self._on_timer_cancel,
                                  self._get_font, self._get_colors)
        # 加载图标
        self.menu_image = ctk.CTkImage(light_image=Image.open(r"task\img\menu.png"), size=(24, 24))
        self.fold_image = ctk.CTkImage(light_image=Image.open(r"task\img\fold.png"), size=(12, 20))
        self.open_image = ctk.CTkImage(light_image=Image.open(r"task\img\open.png"), size=(12, 20))
        self.show_image = ctk.CTkImage(light_image=Image.open(r"task\img\show.png"), size=(16, 12))
        self.add_image = ctk.CTkImage(light_image=Image.open(r"task\img\add.png"), size=(18, 19))
        self.image_name_list = ['home_dark.png', 'set.png', 'help.png', 'vido.png', 'score.png', 'find.png',
                                'error.png', 'give_money.png']
        self.image_list = []
        for name in self.image_name_list:
            self.image_list.append(ctk.CTkImage(light_image=Image.open(rf"task\img\{name}"), size=(20, 20)))

        # ----------------创建菜单页面----------------
        self.navigation_frame = ctk.CTkFrame(self.root, corner_radius=0, fg_color=self.button_hover_color, width=20)
        self.navigation_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(9, weight=1)
        self.open_frame = ctk.CTkFrame(self.root, corner_radius=0, width=0, fg_color=self.frame_fg_color)
        self.open_frame.grid_rowconfigure(0, weight=1)
        self.open_button = ctk.CTkButton(self.open_frame, corner_radius=0, width=10, height=40, border_spacing=10,
                                         text="", font=self.font, image=self.open_image,
                                         fg_color='transparent',
                                         hover_color=self.button_color, anchor="ns",
                                         command=self.reopen_frame)
        self.open_button.grid(row=0, column=0, sticky="ew")
        self.navigation_frame_label = ctk.CTkLabel(self.navigation_frame, text="  MENU   ", image=self.menu_image,
                                                   compound="left", fg_color="transparent",
                                                   font=self.font, anchor="nw")
        self.navigation_frame_label.grid(row=0, column=0, pady=20)
        self.fold_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, width=10, height=40, border_spacing=10,
                                         text='收起\n目录', font=self.font, image=self.fold_image,
                                         fg_color="transparent", text_color=("gray10", "gray90"),
                                         hover_color=self.button_color,
                                         anchor="e", command=self.fold_frame)
        self.fold_button.grid(row=9, column=0, sticky="new")
        self.button_text_list = ["主页", "设置", "帮助", "刷课日志", "测试成绩", "题库查询", "报错日志", "赞助作者"]
        self.button_command_list = [self.show_main, self.show_set, self.show_help,
                                    lambda: self.show_record('刷课'), lambda: self.show_record('成绩'),
                                    self.show_question_bank, self.show_error, self.show_money]
        self.button_name_list = ['home_button', 'set_button', 'help_button', 'vido_button', 'score_button',
                                 'question_bank_button', 'money_button',
                                 self.open_button, self.fold_button]
        for i in range(len(self.button_text_list)):
            self.button_name_list[i] = ctk.CTkButton(self.navigation_frame, corner_radius=10, width=20, height=40,
                                                     border_spacing=10,
                                                     text=self.button_text_list[i], font=self.font,
                                                     image=self.image_list[i],
                                                     fg_color="transparent", text_color='black',
                                                     hover_color=self.button_color, anchor="w",
                                                     command=self.button_command_list[i])
            self.button_name_list[i].grid(row=i + 1, column=0, padx=8, pady=3, sticky="ew")
        self.change_theme = ctk.CTkOptionMenu(self.navigation_frame, values=[i for i in self.color_value_dict.keys()],
                                              width=10, fg_color='#F9F9FA', font=self.font, text_color='black',
                                              dropdown_fg_color=self.frame_fg_color, button_color=self.button_color,
                                              dropdown_hover_color=self.button_color,
                                              button_hover_color=self.button_hover_color,
                                              command=self.change_appearance_mode_event)
        self.change_theme.grid(row=11, column=0,pady=3,sticky="s")
        self.change_theme_value = self.change_theme.get()
        # self.feedback_button = ctk.CTkButton(self.navigation_frame, text="💬 我要验牌",
        #                                      font=self.font,width=10,text_color='black',
        #                                      fg_color=self.button_hover_color,
        #                                      hover_color=self.button_color,
        #                                      command=self._show_feedback_popup)
        # self.feedback_button.grid(row=10, column=0, pady=(20, 2),sticky="s")
        # ----------------标签页----------------
        self.label_frame = ctk.CTkFrame(self.root, fg_color=self.frame_fg_color, corner_radius=0)
        self.label_frame.grid(row=0, column=1, sticky='nsew')

        self.time_label = ctk.CTkLabel(self.label_frame, text="", fg_color='transparent', font=self.font)
        self.time_label.grid(row=0, column=0, columnspan=3, padx=5, pady=2, sticky=tk.W)
        self.announcement_text = ctk.CTkTextbox(self.label_frame, font=self.font,
                                                fg_color='transparent',height=50,width=450)
        self.announcement_text.insert(tk.END, self.announcement)
        self.announcement_text.configure(state=tk.DISABLED)
        self.announcement_text.grid(row=1, column=0, columnspan=3, sticky=tk.W + tk.E, padx=5, pady=0)

        # ---------------- 主页 ----------------
        self.start_button = ctk.CTkButton(self.main_frame, text="▶ 开始刷课", height=40, border_spacing=10,
                                          fg_color=self.button_color,
                                          command=self.start, font=self.font, hover_color=self.button_hover_color)
        self.start_button.grid(row=0, column=0, padx=5, pady=5)
        self.auto_sign = ctk.CTkButton(self.main_frame, text="自动签到", height=40, border_spacing=10,
                                       fg_color=self.button_color,
                                       command=self.start_sign, font=self.font,
                                       hover_color=self.button_hover_color)
        self.auto_sign.grid(row=0, column=1, padx=5, pady=5)
        self.close_button = ctk.CTkButton(self.main_frame, text="■ 结束刷课", height=40, border_spacing=10,
                                          fg_color=self.button_color, hover_color=self.button_hover_color,
                                          command=self.close, font=self.font)
        self.update_button = ctk.CTkButton(self.main_frame, text="↻ 检查更新", height=40, border_spacing=10,
                                           fg_color=self.button_color,
                                           command=self.check_update, font=self.font,
                                           hover_color=self.button_hover_color)
        self.update_button.grid(row=0, column=2, padx=5, pady=5)
        self.text_box_frame= ctk.CTkFrame(self.main_frame, fg_color=self.frame_fg_color, corner_radius=0,width=450)
        self.text_box_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky=tk.W + tk.E + tk.N + tk.S)
        self.text_box = ctk.CTkTextbox(self.text_box_frame,border_width=1,
                                       fg_color='transparent',
                                       height=24 * 20,
                                       width=44 * 10,
                                       font=self.font)
        self.hint_txt='WELCOME TO 学习通刷课 ！！！\n请先进入设置页面填写信息！！！'
        self.hint_label=ctk.CTkLabel(self.text_box_frame,text=self.hint_txt,font=self.font,fg_color='transparent',
                                     width=300,text_color='red')
        self.hint_label.grid(row=0,column=0,sticky=tk.N,pady=5,padx=5)
        self.text_box.grid(row=0, column=0)
        self.frame_name_list = [self.main_frame, self.set_frame, self.help_frame, self.vido_frame,
                                self.score_frame, self.question_bank_frame, self.error_frame, self.money_frame,
                                self.open_frame, self.navigation_frame, self.label_frame,self.text_box_frame]
        # ---------------- 刷课记录 ----------------
        self.course_vido_entry = ctk.CTkComboBox(self.vido_frame, dropdown_font=self.font, values=[],
                                                 dropdown_fg_color=self.frame_fg_color,
                                                 button_color=self.button_color,
                                                 button_hover_color=self.button_hover_color,
                                                 dropdown_hover_color=self.button_color,
                                                 font=self.font, command=lambda value: self.show_record('刷课'))
        self.course_name = self.course_vido_entry.get()
        self.course_vido_entry.grid(row=0, column=0, padx=10, pady=(10, 0), sticky=tk.W + tk.E)
        self.find_button1 = ctk.CTkButton(self.vido_frame, text="查询", command=lambda: self.show_record('刷课'),
                                          fg_color=self.button_color,
                                          font=self.font, hover_color=self.button_hover_color)
        self.find_button1.grid(row=0, column=1, padx=1, pady=(10, 0), sticky=tk.W)
        self.delete_button1 = ctk.CTkButton(self.vido_frame, text="删除记录",
                                            command=lambda: self.delete_record('刷课'), fg_color="#F87171",
                                            hover_color="#EF4444",
                                            font=self.font)
        self.delete_button1.grid(row=0, column=2, padx=1, pady=(10, 0))

        self.progress_frame = ctk.CTkFrame(self.vido_frame, fg_color='transparent', corner_radius=0)
        self.progress_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=(8, 2), sticky=tk.EW)

        self.course_progress_label = ctk.CTkLabel(self.progress_frame, text="", font=ctk.CTkFont(size=12),
                                                  fg_color='transparent', anchor="w")
        self.course_progress_label.pack(side=tk.LEFT, padx=(0, 10))

        self.course_progress_bar = ctk.CTkProgressBar(self.progress_frame, height=8, width=200,
                                                      fg_color=self.button_hover_color,
                                                      progress_color=self.button_color,
                                                      corner_radius=4)
        self.course_progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.course_progress_bar.set(0)

        self.vido_text = ctk.CTkTextbox(self.vido_frame, height=500, width=435, font=self.font, fg_color='transparent')
        self.vido_text.configure(state=tk.DISABLED)
        self.vido_text.grid(row=2, column=0, columnspan=3, padx=10, pady=5, sticky=tk.W + tk.E + tk.N + tk.S)

        # ---------------- 成绩日志 ----------------
        self.course_score_entry = ctk.CTkComboBox(self.score_frame, dropdown_font=self.font, font=self.font, values=[],
                                                  dropdown_fg_color=self.frame_fg_color,
                                                  button_color=self.button_color,
                                                  button_hover_color=self.button_hover_color,
                                                  dropdown_hover_color=self.button_color,
                                                  command=lambda value: self.show_record('成绩'))
        self.course_name = self.course_score_entry.get()
        self.course_score_entry.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W + tk.E)
        self.find_button2 = ctk.CTkButton(self.score_frame, text="查询", command=lambda: self.show_record('成绩'),
                                          fg_color=self.button_color,
                                          font=self.font, hover_color=self.button_hover_color)
        self.find_button2.grid(row=0, column=1, padx=1, pady=5)
        self.delete_button2 = ctk.CTkButton(self.score_frame, text="删除记录",
                                            command=lambda: self.delete_record('成绩'), fg_color="#F87171",
                                            hover_color="#EF4444",
                                            font=self.font)
        self.delete_button2.grid(row=0, column=2, padx=1, pady=5)
        self.score_frame.rowconfigure(0, weight=1)
        self.score_txt = ctk.CTkTextbox(self.score_frame, height=527, width=435, font=self.font, fg_color='transparent')
        self.score_txt.configure(state=tk.DISABLED)
        self.score_txt.grid(row=1, column=0, columnspan=3, padx=10, pady=5,
                            sticky=tk.W + tk.E + tk.N + tk.S)
        self.dit = {'刷课': [self.course_vido_entry, '刷课日志', self.vido_text, self.vido_frame],
                    '成绩': [self.course_score_entry, '测试成绩', self.score_txt, self.score_frame]}

        # ---------------- 题库查询 ----------------
        self.tiku_text = ctk.CTkTextbox(self.question_bank_frame, height=600, width=437, font=self.font,
                                        fg_color='transparent')
        self.tiku_text.configure(state=tk.DISABLED)
        self.tiku_text.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky=tk.W + tk.E + tk.N + tk.S)
        self.delete_tiku_button = ctk.CTkButton(
            self.question_bank_frame, text="删除所有缓存题目", command=self.delete_huancun,
            fg_color="#F87171", hover_color="#EF4444", corner_radius=16, height=36
        )
        self.delete_tiku_button.grid(row=2, column=0, padx=1, pady=5, columnspan=2, sticky=tk.W + tk.E)

        # ---------------- 设置页面（委托给 SettingsPanel） ----------------
        self.style = ttk.Style()
        self.style.configure('TLabelframe', background=self.frame_fg_color, borderwidth=10)
        self.style.configure('TLabelframe.Label', background=self.frame_fg_color, font=self.font)
        self.style.configure('TLabel', background=self.frame_fg_color)
        self.account_info = self.config.load_account()
        self.settings_panel = SettingsPanel(
            self.set_frame, self.config,
            change_font=self.change_font,
            change_text_box=self.change_text_box,
            get_font=self._get_font,
            get_colors=self._get_colors,
            get_theme=self._get_theme,
            show_money=self.show_money,
            root=self.root,
            _timer=self._timer
        )

        self.combobox_lst = [
            self.change_theme, self.course_score_entry, self.course_vido_entry,
        ]
        self.combobox_lst.extend(self.settings_panel.comboboxes)
        self.check_switch = list(self.settings_panel.switches)
        self.button_name_list1 = [self.start_button, self.auto_sign, self.close_button, self.update_button,
                                  self.find_button1, self.find_button2, self.delete_button1, self.delete_button2]
        self.button_name_list1.extend(self.settings_panel.buttons)

        # ---------------- 帮助页面 ----------------
        self.text = self.config.get_help_text()
        self.help_txt = ctk.CTkTextbox(self.help_frame, height=600, width=500, font=self.font, fg_color='transparent')
        self.help_txt.grid(pady=(5,20))
        self.help_txt.insert(tk.END, self.text)
        self.help_txt.configure(state=tk.DISABLED)

        # ---------------- 报错日志 ----------------
        self.error_text = ctk.CTkTextbox(self.error_frame, height=600, width=497, font=self.font, fg_color='transparent')
        self.error_text.configure(state=tk.DISABLED)
        self.error_text.grid(pady=(5,20),row=0,column=0)

        # ---------------- 赞助页面 ----------------
        self.sponsor_panel = SponsorPanel(self.money_frame,self._get_font,self._get_colors,self.root)


        self.process_condition = False
        self._load_data()
        self.show_main()
        self.settings_panel.function_choice()
        if self.user_notice == 'True':
            self.show_user_notice()
        else:
            self.check_update()
        self.change_text_box(self.all_cour,self.multi_device)
        self.update_time()
        if self.timer_active:
            self.hint_txt+=(f"\n定时刷课已开启:\n  开始时间: {self.timer_start_time}\n  "
                                 f"结束时间: {self.timer_end_time}\n"
                                 f"请勿关闭此窗口，否则定时刷课将无法正常开启")
        self.hint_label.configure(text=self.hint_txt)


    # ========== 委托方法（供子模块回调） ==========

    def _get_font(self):
        return (self.account_info.get('font_type', 'Microsoft YaHei'),
                int(self.account_info.get('font_size', 12)))

    def _get_colors(self):
        theme = self.record_color_lst[-1] if self.record_color_lst else '海洋蓝'
        return self.color_value_dict.get(theme, ['#1E88E5', '#F8FAFC', '#90CAF9'])

    def _get_theme(self):
        theme = self.record_color_lst[-1] if self.record_color_lst else '海洋蓝'
        return self.color_value_dict.get(theme, ['#1E88E5', '#F8FAFC', '#90CAF9'])

    def _on_timer_set(self, start_str, end_str):
        self.timer_start_time = start_str
        self.timer_end_time = end_str
        self.timer_active = True
        self.hint_txt+=(     f"\n定时刷课已开启:\n  开始时间: {self.timer_start_time}\n"
                             f"  结束时间: {self.timer_end_time}\n"
                             f"请勿关闭此窗口，否则定时刷课将无法正常开启")
        self.text_box.see(tk.END)
        self.account_info['timer_start'] = start_str
        self.account_info['timer_end'] = end_str
        self.account_info['timer_active']=1

        self.config.save_account(self.account_info)
        self.hint_label.configure(text=self.hint_txt)

    def _on_timer_cancel(self):
        self.timer_active = False
        self.hint_txt+= "\n定时刷课已禁用"
        self.account_info['timer_active']=0
        self.config.save_account(self.account_info)
        self.hint_label.configure(text=self.hint_txt)

    def _load_data(self):
        """加载账户配置和课程数据"""
        try:
            self.account_info = self.config.load_account()
            phone = self.account_info.get('phone_number', '')
            self.data = self.config.load_courses(phone)
            if self.data:
                self.course_score_entry.configure(values=tuple(self.data))
                self.course_vido_entry.configure(values=tuple(self.data))
            self.user_notice = self.account_info.get('user_notice', 'True')
            self.multi_device=self.account_info.get('multi_device',0)
            self.course_score_entry.set(self.account_info.get('cour', [''])[0])
            self.course_vido_entry.set(self.account_info.get('cour', [''])[0])
            self.all_cour=self.account_info.get('cour', [''])
            self.settings_panel.load_data(self.data)
            if self.account_info.get('timer_active'):
                self.timer_active = True
            self.timer_start_time = self.account_info.get('timer_start', '04:00:00')
            self.timer_end_time = self.account_info.get('timer_end', '03:00:00')
        except FileNotFoundError:
            pass


    # ========== 页面导航 ==========

    def delete_record(self, file_name):
        file_path = fr'task\record\《{self.dit[file_name][0].get()}》的{file_name}记录.txt'
        if os.path.exists(file_path):
            yes_no = tk.messagebox.askyesno('确认', '确定要删除吗？删除后无法恢复')
            if yes_no:
                os.remove(file_path)
                tk.messagebox.showinfo('提示', f'{file_name}记录文件已成功删除')
        else:
            tk.messagebox.showwarning('警告', f'指定的{file_name}记录文件不存在')
        self.show_record(file_name)

    def delete_huancun(self):
        try:
            folder_path = r'task/record'
            tiku_files = [f for f in os.listdir(folder_path)
                          if f.endswith('.pkl') and os.path.isfile(os.path.join(folder_path, f))]
            for tiku_file in tiku_files:
                os.remove(os.path.join(folder_path, tiku_file))
            tk.messagebox.showinfo('提示', '缓存记录文件已成功删除')
        except:
            tk.messagebox.showwarning('警告', '删除失败')
        self.show_question_bank()

    # ========== 用户须知（委托） ==========

    def show_user_notice(self):
        UserNotice(self.root, on_confirm=lambda: self.check_update(),
                   on_cancel=self.root.destroy).show()

    # ========== 更新检查（委托） ==========

    def check_update(self):
        self.hint_label.grid(row=0, column=0, sticky=tk.N, pady=5, padx=5)
        self.hint_txt+=self._updater.check()
        self.hint_label.configure(text=self.hint_txt)


    # ========== 定时刷课（委托） ==========
    def start_sign(self):
        if self.check_info():
            SignWindow(self.root, self.account_info, self.font,self.auto_sign,
                   self.button_color, self.button_hover_color)
        # tk.messagebox.showinfo('提示', '自动签到功能已下架，如有需要请联系作者邮箱2022865286@qq.com')
        # self._show_feedback_popup()
    def show_frame(self, frame):
        for f in self.frame_name_list[:8]:
            if f != frame:
                f.grid_forget()
            else:
                f.grid(row=1, column=1, sticky='nsew')

    def show_main(self):
        self.select_frame_by_name('主页')
        self.show_frame(self.main_frame)

    def show_record(self, name):
        self.select_frame_by_name(self.dit[name][1])
        self.dit[name][2].configure(state=tk.NORMAL)
        self.dit[name][2].delete('1.0', tk.END)
        if name == '刷课':
            self.refresh_course_progress()
        try:
            with open(fr'task\record\《{self.dit[name][0].get()}》的{name}记录.txt', 'r', encoding='utf-8') as f:
                content = f.read()
                self.dit[name][2].insert(tk.END, content)
        except FileNotFoundError:
            self.dit[name][2].insert(tk.END, f'暂未查询到《{self.dit[name][0].get()}》的{name}记录')
        self.show_frame(self.dit[name][3])
        self.dit[name][2].configure(state=tk.DISABLED)

    def refresh_course_progress(self):
        course_name = self.course_vido_entry.get()
        try:
            data = self.config.get_course_process()
            if course_name in data:
                done, total = data[course_name]
                pct = done / total if total > 0 else 0
                self.course_progress_label.configure(
                    text=f"课程进度: {pct * 100:.1f}% ",
                )
                self.course_progress_bar.set(pct)
            else:
                self.course_progress_label.configure(text="未查询到该课程的进度")
                self.course_progress_bar.set(0)
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            self.course_progress_label.configure(text="")
            self.course_progress_bar.set(0)

    def show_question_bank(self, *key):
        self.select_frame_by_name('题库查询')
        self.tiku_text.configure(state=tk.NORMAL)
        self.tiku_text.delete('1.0', tk.END)
        try:
            folder_path = r'task/record'
            tiku_files = [f for f in os.listdir(folder_path)
                          if f.endswith('.pkl') and os.path.isfile(os.path.join(folder_path, f))]
            tiku_txt = ''
            for tiku_file in tiku_files:
                if 'ques1' not in tiku_file:
                    continue
                tiku_file_path = os.path.join(folder_path, tiku_file)
                data = pickle.load(open(tiku_file_path, 'rb'))['value']
                tiku_txt += f"问题: {data['question']}\n{data['options']}\n答案为：{data['answer']}\n\n"
            if tiku_txt == '':
                self.tiku_text.insert(tk.END, '暂无缓存的题目')
            self.tiku_text.insert(tk.END, tiku_txt)
        except FileNotFoundError:
            self.tiku_text.insert(tk.END, '暂无缓存的题目')
        self.show_frame(self.question_bank_frame)
        self.tiku_text.configure(state=tk.DISABLED)

    def show_error(self):
        self.select_frame_by_name('报错日志')
        try:
            self.error_text.configure(state=tk.NORMAL)
            with open('error.log', 'r', encoding='utf-8') as f:
                content = f.read()
                self.error_text.delete('1.0', tk.END)
                self.error_text.insert(tk.END, content)
        except FileNotFoundError:
            self.error_text.delete('1.0', tk.END)
            self.error_text.insert(tk.END, '暂无报错记录')
        self.show_frame(self.error_frame)
        self.error_text.configure(state=tk.DISABLED)

    def show_set(self):
        self.select_frame_by_name('设置')
        self.show_frame(self.set_frame)

    def show_money(self):
        self.select_frame_by_name('赞助作者')
        self.show_frame(self.money_frame)

    def show_help(self):
        self.select_frame_by_name('帮助')
        self.show_frame(self.help_frame)

    def select_frame_by_name(self, name):
        for i in range(len(self.button_name_list) - 2):
            txt = self.button_text_list[i]
            self.button_name_list[i].configure(
                fg_color=self.color_value_dict.get(self.change_theme.get())[0] if name == txt else "transparent")

    # ========== 刷课控制 ==========

    def run_program(self, file_name,text_box):
        self.fold_frame()
        text_box.delete('1.0', tk.END)

        def read_output(text_box):
            process = subprocess.Popen(file_name,
                                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.process[process]=text_box
            color_tag = None
            logger.info('======================主程序开始运行======================')
            while True:
                output = process.stdout.readline()
                if output == b'' and process.poll() is not None:
                    break
                if output:
                    try:
                        decoded_output = output.decode()
                    except UnicodeDecodeError:
                        decoded_output = output.decode('gbk', errors='ignore')
                    ansi_color_start = re.search(r'\[(\d+?)m', decoded_output)
                    ansi_color_end = re.search(r'\[0m', decoded_output)
                    if ansi_color_start:
                        ansi_color_code = ansi_color_start.group(1)
                        if ansi_color_code == '91':
                            color_tag = 'red'
                            text_box.tag_config(color_tag, foreground=color_tag)
                            decoded_output = decoded_output.replace(ansi_color_start.group(0), "")
                    if ansi_color_end:
                        color_tag = None
                        decoded_output = decoded_output.replace(ansi_color_end.group(0), "")
                    for colorama_func, tkinter_color in self.colorama_to_tkinter.items():
                        start_pattern = re.escape(getattr(Fore, colorama_func) + '')
                        end_pattern = re.escape(Fore.RESET)
                        color_start = re.search(start_pattern, decoded_output)
                        color_end = re.search(end_pattern, decoded_output)
                        if color_start:
                            color_tag = tkinter_color
                            text_box.tag_config(color_tag, foreground=color_tag)
                            decoded_output = decoded_output.replace(color_start.group(0), "")
                        if color_end:
                            color_tag = None
                            decoded_output = decoded_output.replace(color_end.group(0), "")
                    decoded_output = decoded_output.replace('', '')
                    if color_tag:
                        text_box.insert(tk.END, decoded_output, color_tag)
                    else:
                        text_box.insert(tk.END, decoded_output)
                    decoded_output = re.sub(r'[\n\t\r]', '', decoded_output)
                    if decoded_output.strip():
                        logger.info(decoded_output)
                    if '❌' in decoded_output:
                        self.close()
                    text_box.see(tk.END)
            process.stdout.close()
            try:
                process.wait()
            except:
                pass

        self.thread=threading.Thread(target=read_output,args=(text_box,))
        self.thread.start()

    def check_info(self):
        self.account_info = self.config.load_account()
        if self.account_info['phone_number'] == '':
            tk.messagebox.showerror('警告',
                                    message='请在设置页面填写相关信息再保存，如果已经保存，请在关闭主窗口后，'
                                            '再右键点击刷课程序用管理员权限运行,进入设置页面填写相关信息')
            return False
        return True

    def start(self):
        if self.check_info():
            self.process_condition = True
            self.all_cour=self.account_info['cour']
            self.start_button.grid_forget()
            self.hint_label.grid_forget()
            self.close_button.grid(row=0, column=0, padx=5, pady=5)
            self.file_name = self.account_info['file_name']
            if self.account_info['multi_device']:
                threading.Thread(target=self.mutual_thread).start()
            else:
                threading.Thread(target=self.run_program, args=(self.file_name, self.text_box)).start()

    def mutual_thread(self):
        i=0
        for course in self.all_cour:
            self.account_info['cour'] = [course]
            self.config.save_account(self.account_info)
            self.run_program(self.file_name, self.text_box_lst[i])
            # time.sleep(3)
            # print(self.text_box_lst[i].get("1.0", "end"))
            while '正在登录中...' not in self.text_box_lst[i].get("1.0", "end"):
                time.sleep(1)
            i += 1
        self.account_info['cour'] = self.all_cour
        self.config.save_account(self.account_info)
    def close(self):
        self.process_condition = False
        self.start_button.grid(row=0, column=0, padx=5, pady=10)
        self.close_button.grid_forget()
        self.reopen_frame()
        for process in self.process.keys():
            try:
                if os.name == 'nt':
                    subprocess.run(['taskkill', '/F', '/T', '/PID', str(process.pid)])
                else:
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                self.process[process].insert(tk.END, "程序已成功关闭\n")
                logger.info('======================程序已成功关闭======================')
            except Exception as e:
                self.process[process].insert(tk.END, f"关闭失败: {e}\n")
                logger.error(f"======================程序关闭失败: {e}======================")
        self.process = {}

    def update_time(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        countdown_text = ""
        if self.timer_active:
            now = datetime.now()
            if self.process_condition:
                end_time = datetime.strptime(self.timer_end_time, "%H:%M:%S")
                end_datetime = now.replace(hour=end_time.hour, minute=end_time.minute, second=end_time.second,
                                           microsecond=0)
                if end_datetime < now:
                    end_datetime += timedelta(days=1)
                time_diff = (end_datetime - now).total_seconds()
                hours = int(time_diff // 3600)
                minutes = int((time_diff % 3600) // 60)
                seconds = int(time_diff % 60)
                countdown_text = f" | 距离结束刷课还剩 {hours:02d}小时{minutes:02d}分钟{seconds:02d}秒"
            else:
                start_time = datetime.strptime(self.timer_start_time, "%H:%M:%S")
                start_datetime = now.replace(hour=start_time.hour, minute=start_time.minute, second=start_time.second,
                                             microsecond=0)
                if start_datetime < now:
                    start_datetime += timedelta(days=1)
                time_diff = (start_datetime - now).total_seconds()
                hours = int(time_diff // 3600)
                minutes = int((time_diff % 3600) // 60)
                seconds = int(time_diff % 60)
                countdown_text = f" | 距离开始刷课还剩 {hours:02d}小时{minutes:02d}分钟{seconds:02d}秒"
        self.time_label.configure(text=f"当前时间: {current_time}{countdown_text}")
        self.root.after(1000, self.update_time)
        if self.timer_start_time in current_time and not self.process_condition and self.timer_active:
            self.start()
        if self.timer_end_time in current_time and self.process_condition and self.timer_active:
            self.close()

    def change_font(self):
        self.font = (self.settings_panel.font_entry.get(), int(self.settings_panel.size_entry.get()))
        self.style.configure('TLabelframe.Label', font=self.font)

        def update_font(widget):
            if isinstance(widget, (tk.Label, tk.Button, tk.Text, ttk.Label, tk.Entry, tk.LabelFrame)):
                widget.config(font=self.font)
            elif isinstance(widget, ttk.Checkbutton):
                style = ttk.Style()
                style.configure('TCheckbutton', font=self.font)
                widget.config(style='TCheckbutton')
            for child in widget.winfo_children():
                update_font(child)

        update_font(self.root)

    def change_text_box(self,all_cour,multi_device_check):
        for text_box in self.text_box_lst:
            text_box.grid_forget()
        for lab in self.lab_lst:
            lab.grid_forget()
        self.lab_lst = []
        self.text_box_lst=[]
        if multi_device_check:
            i=0
            self.text_box.grid_forget()
            self.hint_label.grid(row=0, column=0, sticky=tk.N, pady=5, padx=5)
            for course in all_cour:
                text_box=ctk.CTkTextbox(self.text_box_frame,border_width=1,
                                           fg_color='transparent',
                                           height=int(480/len(all_cour)),
                                           width=440,
                                           font=self.font)
                # self.text_box_lst[i].insert(tk.INSERT,course)
                lab=ctk.CTkLabel(self.text_box_frame,text=course,font=self.font,fg_color='transparent')
                self.lab_lst.append(lab)
                self.text_box_lst.append(text_box)
                text_box.grid(row=i,column=0)
                lab.grid(row=i,column=0,sticky=tk.E+tk.N,pady=5,padx=5)
                i+=1
            self.hint_label.lift()

        else:
            self.text_box.grid(row=0, column=0)

    def fold_frame(self):
        self.navigation_frame.grid_forget()
        self.open_frame.grid(row=0, column=0, rowspan=2, sticky="ns")

    def reopen_frame(self):
        self.open_frame.grid_forget()
        self.navigation_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")

    def change_appearance_mode_event(self, theme):
        colors = self.color_value_dict.get(theme, ['#1E88E5', '#F8FAFC', '#90CAF9'])
        self.record_color_lst.append(theme)
        for frame in self.frame_name_list:
            frame.configure(fg_color=self.color_value_dict.get(theme)[1])
        self.navigation_frame.configure(fg_color=self.color_value_dict.get(theme)[2])
        self.style.configure('TLabelframe', background=self.color_value_dict.get(theme)[1])
        self.style.configure('TLabelframe.Label', background=self.color_value_dict.get(theme)[1])
        self.style.configure('TLabel', background=self.color_value_dict.get(theme)[1])
        for check in self.check_switch:
            check.configure(bg_color=colors[1], progress_color=colors[0])
        for button in self.button_name_list1:
            button.configure(fg_color=self.color_value_dict.get(theme)[0],
                             hover_color=self.color_value_dict.get(theme)[2])
        for combox in self.combobox_lst:
            combox.configure(dropdown_fg_color=self.color_value_dict.get(theme)[1],
                             dropdown_hover_color=self.color_value_dict.get(theme)[0], bg_color='transparent',
                             button_color=self.color_value_dict.get(theme)[0],
                             button_hover_color=self.color_value_dict.get(theme)[2])
        self.sponsor_panel.update_theme(colors)
        self.course_progress_bar.configure(progress_color=colors[0], fg_color=colors[2])
        self.course_progress_label.configure(text_color=colors[0])
        for i in range(len(self.button_name_list)):
            if self.button_name_list[i].cget('fg_color') == \
                    self.color_value_dict.get(self.record_color_lst[len(self.record_color_lst) - 2])[0]:
                self.button_name_list[i].configure(fg_color=self.color_value_dict.get(theme)[0])
            self.button_name_list[i].configure(hover_color=self.color_value_dict.get(theme)[0])

if __name__ == "__main__":
    start = Start()
    start.root.mainloop()