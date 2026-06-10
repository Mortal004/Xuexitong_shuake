# Copyright (c) 2025 Mortal004
# All rights reserved.
# This software is provided for non-commercial use only.
# For more information, see the LICENSE file in the root directory of this project.
#激活环境start_venv\Scripts\activate
#打包python -m PyInstaller --onefile --noconsole start.py
#python -m PyInstaller --onefile --noconsole --icon=xuexitong.ico start.py
import json
import random
import signal
import time
from datetime import datetime
import re
import threading
import tkinter as tk
import subprocess
from PIL import Image
from colorama import Fore
from tkinter import ttk, messagebox, filedialog
import requests
import os
import customtkinter as ctk
import pickle
import logging # For logging
class ToolTip:
    """简单的悬停提示类"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind('<Enter>', self.show_tip)
        self.widget.bind('<Leave>', self.hide_tip)

    def show_tip(self, event=None):
        # 获取鼠标指针的屏幕坐标
        x = self.widget.winfo_pointerx() + 10
        y = self.widget.winfo_pointery() + 10
        self.tip_window = tk.Toplevel(self.widget)
        self.tip_window.wm_overrideredirect(True)
        self.tip_window.wm_geometry(f"+{x}+{y}")
        self.tip_window.wm_attributes("-topmost", True)

        label = tk.Label(self.tip_window, text=self.text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1,
                         font=("微软雅黑", 10))
        label.pack()

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

    def set_text(self, new_text):
        """动态修改提示文本"""
        self.text = new_text
# 设置日志配置
logging.basicConfig(
    level=logging.INFO,  # 设置日志级别为 DEBUG，以便捕获更多信息
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("输出记录.log", encoding='utf-8'), # 写入文件
        # logging.StreamHandler(sys.stdout) # 同时输出到控制台
    ]
)
logger = logging.getLogger(__name__)
class Start:
    def __init__(self):
        self.timer_active = False
        self.timer_end_time = '03:00:00'
        self.timer_start_time = '04:00:00'
        self.dynamic_rows = []
        self.process = None
        self.colorama_to_tkinter = {
            'RED': 'red',
            'YELLOW': 'yellow',
            'BLUE': 'blue',
            'GREEN': 'green',
            'MAGENTA': 'magenta'
        }
        self.color_value_dict={
            '海洋蓝': ['#1E88E5', '#E3F2FD', '#81AED1'],
            '清新绿': ['#2E7D32', '#E8F5E9', '#A5D6A7'],
            '暖阳橙': ['#F57C00', '#FFF3E0', '#FFB74D'],
            '淡雅灰': ['#607D8B', '#ECEFF1', '#B0BEC5'],
            '天空湖': ['#00838F', '#E0F7FA', '#80DEEA'],
            '深邃夜': ['#2C3E50', '#ECF0F1', '#BDC3C7'],
            '紫罗兰': ['#6A1B9A', '#F3E5F5', '#CE93D8']}# 颜色值字典[深，浅,中]
        self.font = ("Helvetica", 13)
        self.record_color_lst= ['海洋蓝']

        self.frame_fg_color = self.color_value_dict[self.record_color_lst[0]][1]
        self.button_color = self.color_value_dict[self.record_color_lst[0]][0]
        self.button_hover_color = self.color_value_dict[self.record_color_lst[0]][2]
        self.root = ctk.CTk()
        ctk.set_appearance_mode("light")
        self.root.geometry("+1050+20")  # 设置窗口大小
        with open(r'task/tool/version_info','r',encoding='utf-8') as f:
            version_info=f.read()
            self.root.title(f'学习通刷课 {version_info}')
        # 初始设定窗口置顶
        self.is_topmost = True
        self.root.wm_attributes("-topmost", self.is_topmost)
        self.main_frame =  ctk.CTkFrame(self.root,fg_color=self.frame_fg_color,corner_radius=0)
        self.set_frame =  ctk.CTkFrame(self.root,fg_color=self.frame_fg_color,corner_radius=0)
        self.help_frame =  ctk.CTkFrame(self.root,fg_color=self.frame_fg_color,corner_radius=0)
        self.vido_frame =  ctk.CTkFrame(self.root,fg_color=self.frame_fg_color,corner_radius=0)
        self.score_frame = ctk.CTkFrame(self.root,fg_color=self.frame_fg_color,corner_radius=0)
        self.question_bank_frame=ctk.CTkFrame(self.root,fg_color=self.frame_fg_color,corner_radius=0)
        self.error_frame=  ctk.CTkFrame(self.root,fg_color=self.frame_fg_color,corner_radius=0)
        self.money_frame =  ctk.CTkFrame(self.root,fg_color=self.frame_fg_color,corner_radius=0)
        self.root.resizable(False, False)  # 禁止用户调整窗口大小
         # 使用ico格式的图标文件
        self.root.iconbitmap(r'task\img\xuexitong1 .ico')
        self.root.attributes('-alpha', 1)

        # 加载图标
        self.menu_image = ctk.CTkImage(light_image=Image.open(r"task\img\menu.png"), size=(24, 24))
        self.fold_image = ctk.CTkImage(light_image=Image.open(r"task\img\fold.png"), size=(12, 20))
        self.open_image = ctk.CTkImage(light_image=Image.open(r"task\img\open.png"), size=(12, 20))
        self.show_image = ctk.CTkImage(light_image=Image.open(r"task\img\show.png"), size=(16, 12))
        self.add_image  = ctk.CTkImage(light_image=Image.open(r"task\img\add.png"), size=(18, 19))
        self.image_name_list = ['home_dark.png', 'set.png', 'help.png', 'vido.png', 'score.png', 'find.png',
                                'error.png', 'give_money.png']
        self.image_list = []
        for name in self.image_name_list:
            self.image_list.append(ctk.CTkImage(light_image=Image.open(rf"task\img\{name}"), size=(20, 20)))

        # ----------------创建菜单页面----------------
        self.navigation_frame = ctk.CTkFrame(self.root, corner_radius=0,fg_color=self.button_hover_color,width=20)
        self.navigation_frame.grid(row=0, column=0,rowspan=2, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(9, weight=1)
        #----------------展开页面----------------
        self.open_frame= ctk.CTkFrame(self.root, corner_radius=0,width=0,fg_color=self.frame_fg_color)
        #设置权重
        self.open_frame.grid_rowconfigure(0, weight=1)
        self.open_button = ctk.CTkButton(self.open_frame, corner_radius=0,width=10,height=40, border_spacing=10,
                                                   text="",font=self.font,image=self.open_image,
                                                    fg_color='transparent',
                                                   hover_color=self.button_color, anchor="ns",
                                                   command=self.reopen_frame)
        self.open_button.grid(row=0, column=0, sticky="ew")
        # 创建文件菜单并添加选项
        self.navigation_frame_label = ctk.CTkLabel(self.navigation_frame, text="  MENU   ",image=self.menu_image,
                                                             compound="left",fg_color="transparent",
                                                             font=self.font,anchor="nw")
        self.navigation_frame_label.grid(row=0, column=0, pady=20)
        self.fold_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, width=10, height=40, border_spacing=10,
                                         text='收起\n目录', font=self.font, image=self.fold_image,
                                         fg_color="transparent", text_color=("gray10", "gray90"),
                                         hover_color=self.button_color,
                                         anchor="e", command=self.fold_frame)
        self.fold_button.grid(row=9, column=0, sticky="new")
        self.button_text_list = ["主页","设置","帮助","刷课日志","测试成绩","题库查询","报错日志","赞助作者"]
        self.button_command_list = [self.show_main, self.show_set, self.show_help, lambda:self.show_record('刷课'), lambda:self.show_record('成绩'), self.show_question_bank, self.show_error, self.show_money]
        self.button_name_list = ['home_button','set_button','help_button','vido_button','score_button','question_bank_button','error_button','money_button',self.open_button,self.fold_button]
        for i in range(len(self.button_text_list)):
            self.button_name_list[i] = ctk.CTkButton(self.navigation_frame, corner_radius=10,width=20,height=40, border_spacing=10,
                                                   text=self.button_text_list[i],font=self.font,image=self.image_list[i],
                                                   fg_color="transparent", text_color='black',
                                                   hover_color=self.button_color, anchor="w",
                                                    command=self.button_command_list[i])
            self.button_name_list[i].grid(row=i+1, column=0,padx=8, pady=3,sticky="ew")
        self.change_theme = ctk.CTkOptionMenu(self.navigation_frame,values=[i for i in self.color_value_dict.keys()],
                                                width=10,fg_color='#F9F9FA',font=self.font,text_color='black',
                                                dropdown_fg_color=self.frame_fg_color,button_color=self.button_color,
                                                dropdown_hover_color=self.button_color,button_hover_color=self.button_hover_color,
                                                command=self.change_appearance_mode_event)
        self.change_theme.grid(row=10, column=0, pady=20, sticky="s")
        self.change_theme_value = self.change_theme.get()

        #----------------标签页----------------
        self.label_frame=ctk.CTkFrame(self.root,fg_color=self.frame_fg_color,corner_radius=0)
        self.label_frame.grid(row=0,column=1,sticky='nsew')
        self.frame_name_list=[self.main_frame,self.set_frame,self.help_frame,self.vido_frame,
                              self.score_frame,self.question_bank_frame,self.error_frame,self.money_frame,
                              self.open_frame,self.navigation_frame,self.label_frame]
        #  当前时间显示
        self.time_label = ctk.CTkLabel(self.label_frame, text="", fg_color='transparent', font=self.font)
        self.time_label.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)
        #声明
        self.copyright_label = ctk.CTkLabel(self.label_frame,font=self.font,
                                            text="注意：该脚本不可用作商用,使用该脚本产生的任何后果由使用者\n"
                                                 "自行承担,开发者不承担任何责任", fg_color='transparent')
        self.copyright_label.grid(row=1, column=0, columnspan=2, sticky=tk.W+tk.E)

        # ---------------- 主页 ----------------
        # 启动程序按钮
        self.start_button = ctk.CTkButton(self.main_frame, text="▶ 开始刷课",height=40, border_spacing=10,fg_color=self.button_color,
                                          command=self.start, font=self.font,hover_color=self.button_hover_color)
        self.start_button.grid(row=0, column=0,padx=5, pady=10)
        # 定时刷课按钮
        self.timer_button = ctk.CTkButton(self.main_frame, text="⏰ 定时刷课", height=40, border_spacing=10,
                                          fg_color=self.button_color,
                                          command=self.open_timer_window, font=self.font,
                                          hover_color=self.button_hover_color)
        self.timer_button.grid(row=0, column=1, padx=5, pady=10)
        # 关闭程序按钮
        self.close_button = ctk.CTkButton(self.main_frame, text="■ 结束刷课",height=40, border_spacing=10,fg_color=self.button_color, hover_color=self.button_hover_color,
                                          command=self.close,font=self.font)
        # self.close_button.grid(row=0, column=1,padx=5,  pady=10)
        #更新
        self.update_button = ctk.CTkButton(self.main_frame, text="↻ 检查更新",height=40, border_spacing=10,fg_color=self.button_color,
                                           command=self.check_update,font=self.font,hover_color=self.button_hover_color)
        self.update_button.grid(row=0, column=2,padx=5,  pady=10)
        # 创建只读文本框#202022
        self.text_box = ctk.CTkTextbox(self.main_frame,
                                       fg_color='transparent',
                                       height=24 * 20,  # CTkTextbox 使用像素单位
                                       width=40 * 10,  # 需要根据字符宽度估算
                                       font=self.font)
        self.text_box.insert(tk.INSERT, 'WELCOME TO 学习通刷课 ！！！\n请先进入设置页面填写信息！！！')

        # 配置标签样式
        self.text_box.tag_config("center", justify='center')
        self.text_box.tag_add("center", "1.0", "end")
        self.text_box.tag_config("red", foreground="red")
        self.text_box.tag_add("red", "1.0", "end")

        # CTkTextbox 需要额外设置边框颜色（可选）
        self.text_box.configure(border_color='gray', border_width=1)
        self.text_box.configure( state=tk.DISABLED)
        self.text_box.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky=tk.W+tk.E+tk.N+tk.S)

        # ---------------- 刷课记录 ----------------
        # 下拉选项框（包含可输入部分）
        self.course_vido_entry = ctk.CTkComboBox(self.vido_frame, dropdown_font=self.font, values=[],
                                                 dropdown_fg_color=self.frame_fg_color,
                                                 button_color=self.button_color,
                                                 button_hover_color=self.button_hover_color,
                                                 dropdown_hover_color=self.button_color,
                                                 font=self.font, command=lambda value:self.show_record('刷课'))
        # self.course_vido_entry['state'] = 'normal'
        self.course_name = self.course_vido_entry.get()
        self.course_vido_entry.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W + tk.E)  # 使用 sticky 参数使组件填满整个单元格
        # 按钮
        self.find_button1 = ctk.CTkButton(self.vido_frame, text="查询", command=lambda:self.show_record('刷课'), fg_color=self.button_color,
                                          font=self.font, hover_color=self.button_hover_color)
        self.find_button1.grid(row=0, column=1, padx=1, pady=5, sticky=tk.W)  # 使用 sticky 参数使组件填满整个单元格
        self.delete_button1 = ctk.CTkButton(self.vido_frame, text="删除记录",
                                            command=lambda: self.delete_record('刷课'), fg_color="#F87171", hover_color="#EF4444",
                                            font=self.font)
        self.delete_button1.grid(row=0, column=2, padx=1, pady=5)
        # 配置按钮框架的列权重，使按钮居中
        self.score_frame.rowconfigure(0, weight=1)
        # self.score_frame.columnconfigure(1, weight=1)
        #创建只读文本框
        self.vido_text = ctk.CTkTextbox(self.vido_frame, height=527, width=435,font=self.font,fg_color='transparent')
        self.vido_text.configure(state=tk.DISABLED)
        self.vido_text.grid(row=1, column=0, columnspan=3, padx=10, pady=5, sticky=tk.W+tk.E+tk.N+tk.S)

        # ---------------- 成绩日志 ----------------
        # 下拉选项框（包含可输入部分）
        self.course_score_entry = ctk.CTkComboBox(self.score_frame, dropdown_font=self.font, font=self.font, values=[],
                                                  dropdown_fg_color=self.frame_fg_color,
                                                  button_color=self.button_color,
                                                  button_hover_color=self.button_hover_color,
                                                  dropdown_hover_color=self.button_color,
                                                  command=lambda value:self.show_record('成绩'))

        # self.course_score_entry['state'] = 'normal'
        self.course_name=self.course_score_entry.get()
        self.course_score_entry.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W+tk.E)  # 使用 sticky 参数使组件填满整个单元格
        # 按钮
        self.find_button2 = ctk.CTkButton(self.score_frame, text="查询", command=lambda:self.show_record('成绩'), fg_color=self.button_color,
                                          font=self.font, hover_color=self.button_hover_color)
        self.find_button2.grid(row=0, column=1, padx=1, pady=5)  # 使用 sticky 参数使组件填满整个单元格
        self.delete_button2=ctk.CTkButton(self.score_frame, text="删除记录", command=lambda: self.delete_record('成绩'), fg_color="#F87171", hover_color="#EF4444",
                                          font=self.font)
        self.delete_button2.grid(row=0, column=2, padx=1, pady=5)
        # 配置按钮框架的列权重，使按钮居中
        self.score_frame.rowconfigure(0, weight=1)
        # self.score_frame.columnconfigure(1, weight=1)
        # 创建只读文本框
        self.score_txt = ctk.CTkTextbox(self.score_frame,height=527,width=435,font=self.font,fg_color='transparent')
        self.score_txt.configure(state=tk.DISABLED)
        self.score_txt.grid(row=1, column=0, columnspan=3, padx=10, pady=5, sticky=tk.W+tk.E+tk.N+tk.S)  # 使用 sticky 参数使组件填满整个单元格
        self.dit={'刷课':[self.course_vido_entry,'刷课日志',self.vido_text,self.vido_frame],'成绩':[self.course_score_entry,'测试成绩',self.score_txt,self.score_frame]}

        # ---------------- 题库查询 ----------------
        self.tiku_text = ctk.CTkTextbox(self.question_bank_frame, height=600, width=437,font=self.font,fg_color='transparent')
        self.tiku_text.configure(state=tk.DISABLED)
        self.tiku_text.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky=tk.W+tk.E+tk.N+tk.S)
        self.delete_tiku_button = ctk.CTkButton(
            self.question_bank_frame, text="删除所有缓存题目", command=self.delete_huancun,
            fg_color="#F87171", hover_color="#EF4444", corner_radius=16, height=36
        )
        self.delete_tiku_button.grid(row=2, column=0, padx=1, pady=5,columnspan=2,sticky=tk.W+tk.E)

        # ---------------- 设置 ----------------
        # ========== 设置页面（改用CTkFrame模拟分组） ==========
        # 配置设置组
        self.style = ttk.Style()
        self.style.configure('TLabelframe', background=self.frame_fg_color, borderwidth=10)
        self.style.configure('TLabelframe.Label', background=self.frame_fg_color, font=self.font)
        self.style.configure('TLabel', background=self.frame_fg_color)
        self.configuration_set_frame = ctk.CTkFrame(self.set_frame, corner_radius=12, border_width=1,
                                                    fg_color='transparent',
                                                    border_color="#CBD5E1")
        self.configuration_set_frame.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        lbl_cfg = ctk.CTkLabel(self.configuration_set_frame, text="⚙ 配置设置", font=("Microsoft YaHei", 13, "bold"))
        lbl_cfg.grid(row=0, column=0, columnspan=3, sticky="w", padx=12, pady=(8, 4))

        ctk.CTkLabel(self.configuration_set_frame, text="浏览器:", font=self.font).grid(row=1, column=0, padx=6,
                                                                                        pady=4, sticky="w")
        self.browser_entry = ctk.CTkComboBox(
            self.configuration_set_frame, values=['不指定浏览器', 'edge', 'chrome'],
            state='readonly', font=self.font, corner_radius=6, dropdown_fg_color=self.frame_fg_color,
                                           dropdown_hover_color=self.button_color,command=self.auto_fill_browser_driver,
            button_color=self.button_color, button_hover_color=self.button_hover_color
        )
        self.browser_entry.grid(row=1, column=1, padx=6, pady=4, sticky="w")

        ctk.CTkLabel(self.configuration_set_frame, text="驱动地址:", font=self.font).grid(row=2, column=0, padx=6,
                                                                                          pady=4, sticky="w")
        self.browser_driver_entry = ctk.CTkEntry(self.configuration_set_frame, corner_radius=6, width=140)
        self.browser_driver_entry.grid(row=2, column=1, padx=6, pady=4, sticky="w")
        self.open_file_button = ctk.CTkButton(
            self.configuration_set_frame, text="选择文件", width=120,
            fg_color=self.button_color, hover_color=self.button_hover_color, corner_radius=6,
            command=self.select_file
        )
        self.open_file_button.grid(row=3, column=1, padx=6, pady=4, sticky="w")

        # 界面设置组
        self.frame_set_frame = ctk.CTkFrame(self.set_frame, corner_radius=12, border_width=1, fg_color='transparent',
                                            border_color="#CBD5E1")
        self.frame_set_frame.grid(row=1, column=0, sticky="nsew", padx=6, pady=6)
        lbl_ui = ctk.CTkLabel(self.frame_set_frame, text="🎨 界面设置", font=("Microsoft YaHei", 13, "bold"))
        lbl_ui.grid(row=0, column=0, columnspan=3, sticky="w", padx=6, pady=(8, 4))

        ctk.CTkLabel(self.frame_set_frame, text="字体设置:", font=self.font).grid(row=1, column=0, padx=6, pady=4,
                                                                              sticky="w")
        self.font_entry = ctk.CTkComboBox(
            self.frame_set_frame, values=["Helvetica", "Microsoft YaHei",'微软雅黑', '宋体', '楷体', '黑体'],dropdown_fg_color=self.frame_fg_color,
                                           dropdown_hover_color=self.button_color,
            state='readonly', font=self.font, corner_radius=6,
            button_color=self.button_color, button_hover_color=self.button_hover_color
        )
        self.font_entry.grid(row=1, column=1, padx=6, pady=4, sticky="w")

        ctk.CTkLabel(self.frame_set_frame, text="大小设置:", font=self.font).grid(row=2, column=0, padx=6, pady=4,
                                                                              sticky="w")
        self.size_entry = ctk.CTkComboBox(
            self.frame_set_frame, values=['9', '10', '11', '12', '13', '14', '15', '16'], dropdown_fg_color=self.frame_fg_color,
                                           dropdown_hover_color=self.button_color,
            state='readonly', font=self.font, corner_radius=6,
            button_color=self.button_color, button_hover_color=self.button_hover_color
        )
        self.size_entry.grid(row=2, column=1, padx=6, pady=4, sticky="w")

        ctk.CTkLabel(self.frame_set_frame, text="窗口置顶:", font=self.font).grid(row=3, column=0, padx=12, pady=4,
                                                                                  sticky="w")
        self.topmost_check = ctk.CTkSwitch(self.frame_set_frame, text="", command=self.toggle_topmost)
        self.topmost_check.grid(row=3, column=1, padx=6, pady=4, sticky="w")
        self.topmost_check.select()

        # 信息设置组
        self.message_set_frame = ctk.CTkFrame(self.set_frame, corner_radius=12, border_width=1, fg_color='transparent',
                                              border_color="#CBD5E1")
        self.message_set_frame.grid(row=2, column=0, sticky="nsew", padx=6, pady=6)
        lbl_info = ctk.CTkLabel(self.message_set_frame, text="🔐 账号信息", font=("Microsoft YaHei", 13, "bold"))
        lbl_info.grid(row=0, column=0, columnspan=3, sticky="w", padx=6, pady=(8, 4))

        ctk.CTkLabel(self.message_set_frame, text="账号:", font=self.font).grid(row=1, column=0, padx=6, pady=4,
                                                                                sticky="w")
        self.phone_number_entry = ctk.CTkEntry(self.message_set_frame, corner_radius=6, width=140)
        self.phone_number_entry.grid(row=1, column=1, padx=6, pady=4, sticky="w")

        ctk.CTkLabel(self.message_set_frame, text="密码:", font=self.font).grid(row=2, column=0, padx=6, pady=4,
                                                                                sticky="w")
        self.password_entry = ctk.CTkEntry(self.message_set_frame, show='*', corner_radius=6, width=140,)
        self.password_entry.grid(row=2, column=1, padx=(6,0), pady=4, sticky="w")
        self.show_password_button = ctk.CTkButton(self.message_set_frame, text="", fg_color='transparent',
                                                  image=self.show_image,
                                                  command=self.show_password, font=self.font, width=5, height=10)
        self.show_password_button.grid(row=2, column=2,padx=0, pady=4, sticky=tk.E)
        ctk.CTkLabel(self.message_set_frame, text="课程名称:", font=self.font).grid(row=3, column=0, padx=6, pady=4,
                                                                                    sticky="w")
        self.cour_entry = ctk.CTkComboBox(
            self.message_set_frame, values=[], state='normal',dropdown_fg_color=self.frame_fg_color,
                                           dropdown_hover_color=self.button_color,
            font=self.font, corner_radius=6, button_color=self.button_color
        )
        self.cour_entry.grid(row=3, column=1, padx=6, pady=4, sticky="w")
        self.next_row = 4
        self.add_course_button = ctk.CTkButton(self.message_set_frame, text="", fg_color='transparent',
                                                  image=self.add_image,
                                                  command=lambda: self.add_course(''), width=5, height=5)
        self.add_course_button.grid(row=3, column=2, padx=1, pady=4, sticky=tk.E)
        ToolTip(self.add_course_button, "添加课程")

        # 功能设置组（右侧大区域）
        self.function_set_frame = ctk.CTkFrame(self.set_frame, corner_radius=12, border_width=1, fg_color='transparent',
                                               border_color="#CBD5E1")
        self.function_set_frame.grid(row=0, column=1, sticky="nsew", padx=6, pady=6)
        lbl_func = ctk.CTkLabel(self.function_set_frame, text="🚀 功能设置", font=("Microsoft YaHei", 13, "bold"))
        lbl_func.grid(row=0, column=0, columnspan=2, sticky="w", padx=6, pady=(8, 4))

        self.radio_var = tk.IntVar(value=1)
        self.radio_button_1 = ctk.CTkRadioButton(
            self.function_set_frame, text="自动刷课答题", variable=self.radio_var, value=1,
            command=self.function_choice, font=self.font
        )
        self.radio_button_2 = ctk.CTkRadioButton(
            self.function_set_frame, text="自动完成作业", variable=self.radio_var, value=2,
            command=self.function_choice, font=self.font
        )
        self.radio_button_3 = ctk.CTkRadioButton(
            self.function_set_frame, text="自动完成考试", variable=self.radio_var, value=3,
            command=self.function_choice, font=self.font
        )
        self.radio_button_1.grid(row=1, column=1, columnspan=3, padx=12, pady=6, sticky="w")
        self.radio_button_2.grid(row=2, column=1, columnspan=3, padx=12, pady=6, sticky="w")
        self.radio_button_3.grid(row=3, column=1, columnspan=3, padx=12, pady=6, sticky="w")

        # 高级设置组（右侧大区域）
        self.pady=7
        self.detail_set_frame = ctk.CTkFrame(self.set_frame, corner_radius=12, border_width=1, fg_color='transparent',
                                             border_color="#CBD5E1")
        self.detail_set_frame.grid(row=1, column=1, rowspan=2, sticky="nsew", padx=6, pady=6)
        lbl_func = ctk.CTkLabel(self.detail_set_frame, text="🔧 高级设置", font=("Microsoft YaHei", 13, "bold"))
        lbl_func.grid(row=0, column=0, columnspan=2, sticky="w", padx=6, pady=(8, 4))
        # 后续控件动态添加，保持原有变量名
        self.question_label = ctk.CTkLabel(self.detail_set_frame, text="章节测验:", font=self.font)
        self.question_entry = ctk.CTkComboBox(
            self.detail_set_frame, values=["DeepSeek AI", '随机答题', "不刷题"],dropdown_fg_color=self.frame_fg_color,
                                           dropdown_hover_color=self.button_color,
            font=self.font, corner_radius=6, state='readonly',
            button_color=self.button_color, command=self.shua_ti_choice
        )
        #答完题后
        self.after_finish_question=ctk.CTkLabel(self.detail_set_frame, text="答完题后:", font=self.font)
        self.after_finish_question_entry = ctk.CTkComboBox(self.detail_set_frame, values=["仅自动保存", '强制自动提交',
        '搜到60%的题自动提交','搜到70%的题自动提交','搜到80%的题自动提交','搜到90%的题自动提交',  '搜到100%的题自动提交'], dropdown_fg_color=self.frame_fg_color,
                                                           dropdown_hover_color=self.button_color,
                                                           font=self.font, corner_radius=6, state='readonly',
                                                           button_color=self.button_color
                                                           )
        self.vido_question_label = ctk.CTkLabel(self.detail_set_frame, text="视频题目:", font=self.font)
        self.vido_question_entry = ctk.CTkComboBox(
            self.detail_set_frame, values=["DeepSeek AI", '随机答题'],dropdown_fg_color=self.frame_fg_color,
                                           dropdown_hover_color=self.button_color,
            font=self.font, corner_radius=6, state='readonly',
            button_color=self.button_color, command=lambda _: self.shua_ti_choice('视频题目')
        )
        self.discussion_label = ctk.CTkLabel(self.detail_set_frame, text="讨论:", font=self.font)
        self.discussion_entry = ctk.CTkComboBox(
            self.detail_set_frame, values=["DeepSeek AI", '跳过讨论'],dropdown_fg_color=self.frame_fg_color,
                                           dropdown_hover_color=self.button_color,
            font=self.font, corner_radius=6, state='readonly',
            button_color=self.button_color, command=lambda _: self.shua_ti_choice('讨论')
        )
        self.speed_label = ctk.CTkLabel(self.detail_set_frame, text="倍速设置:", font=self.font)
        self.speed_entry = ctk.CTkComboBox(
            self.detail_set_frame, values=['1', '2', '3', '4', '5', '6', '8', '10', '16'],dropdown_fg_color=self.frame_fg_color,
                                           dropdown_hover_color=self.button_color,
            font=self.font, corner_radius=6, state='readonly', command=self.hint,
            button_color=self.button_color
        )
        self.API_label = ctk.CTkLabel(self.detail_set_frame, text="API Key:", font=self.font)
        self.API_entry = ctk.CTkEntry(self.detail_set_frame, show='*', corner_radius=6)
        ToolTip(self.API_entry, "可通过赞助作者获取或者前往deepseek官网购买")
        self.show_api_button = ctk.CTkButton(self.detail_set_frame, text="", fg_color='transparent',
                                             image=self.show_image,
                                             command=self.show_api, font=self.font, width=5, height=10)
        self.pass_face_label = ctk.CTkLabel(self.detail_set_frame, text="跳过人脸:", font=self.font)
        self.pass_face_check = ctk.CTkSwitch(self.detail_set_frame, text="")
        ToolTip(self.pass_face_check, "只有当你的课程需要人脸认证时才开启")
        self.lock_screen_label = ctk.CTkLabel(self.detail_set_frame, text="防锁屏:", font=self.font)
        self.lock_screen_check = ctk.CTkSwitch(self.detail_set_frame, text="")
        self.homework_label = ctk.CTkLabel(self.detail_set_frame, text="选择作业:", font=self.font)
        self.homework_entry = ctk.CTkComboBox(
            self.detail_set_frame, values=['手动选择', '自动选择'],dropdown_fg_color=self.frame_fg_color,
                                           dropdown_hover_color=self.button_color,
            state='readonly', font=self.font, corner_radius=6, command=self.prompt,
            button_color=self.button_color
        )
        # 保存按钮
        self.save_button = ctk.CTkButton(
            self.set_frame, text="💾 保存设置", command=self.save,
            font=("Microsoft YaHei", 13, "bold"), height=40, corner_radius=20,
            fg_color=self.button_color,
            hover_color=self.button_hover_color)
        self.save_button.grid(row=3, column=0, columnspan=2, pady=20, padx=12)

        #设置网格权重
        self.set_frame.rowconfigure(3,weight=1)
        self.frame_set_frame.rowconfigure(3,weight=1)
        self.combobox_lst = [
            self.change_theme, self.speed_entry, self.question_entry, self.cour_entry,
            self.size_entry, self.homework_entry, self.font_entry, self.browser_entry,
            self.course_score_entry, self.course_vido_entry, self.vido_question_entry,
            self.discussion_entry,self.after_finish_question_entry
        ]
        self.check_switch=[self.topmost_check,self.pass_face_check,self.lock_screen_check]
        self.button_name_list1=[self.start_button,self.timer_button, self.close_button, self.update_button, self.save_button,
                                self.open_file_button, self.find_button1, self.find_button2,self.delete_button1,self.delete_button2]

        #----------------帮助页面----------------
        with open(r'task\tool\Help.txt', 'r', encoding='utf-8') as f:
            self.text = f.read()
        self.help_txt = ctk.CTkTextbox(self.help_frame,height=600,width=500,font=self.font,fg_color='transparent')
        self.help_txt.grid(pady=20)
        self.help_txt.insert(tk.END, self.text)
        self.help_txt.configure(state=tk.DISABLED)


        #----------------报错日志----------------
        self.error_text = ctk.CTkTextbox(self.error_frame, height=600, width=497,font=self.font,fg_color='transparent')
        self.error_text.configure(state=tk.DISABLED)
        self.error_text.grid(pady=20)

        #----------------赞助页面----------------
        self.label1 = ctk.CTkLabel(self.money_frame, text="如果对您有帮助，欢迎给我打赏\n各位的支持就是我更新的最大动力\n"
                                                          "邮箱地址：2022865286@qq.com\n(获取API的赞助完后一定要发送邮箱告知作者)",
                                   font=self.font,fg_color='transparent')
        self.label1.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky=tk.W)
        # 加载图片
        self.image = Image.open(r"task/img/money.png")
        self.photo =ctk.CTkImage(self.image,size=(330,350))

        # 创建标签并显示图片
        self.label = ctk.CTkLabel(self.money_frame,text='' ,image=self.photo,fg_color='transparent')
        self.label.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky=tk.W+tk.E)

        # 更新时间显示
        self.process_condition=False
        self.update_time()
        self.load_data()
        self.show_main()
        self.function_choice()
        if self.user_notice=='True':
            # 在初始化完成后显示用户须知弹窗
            self.show_user_notice()
        else:
            self.check_update()
        if self.timer_active:
            self.text_box.configure(state=tk.NORMAL)
            self.text_box.insert(tk.END,
                                 f"\n定时刷课已开启:\n  开始时间: {self.timer_start_time}\n  "
                                 f"结束时间: {self.timer_end_time}\n"
                                 f"请勿关闭此窗口，否则定时刷课将无法正常开启")
    def add_course(self, cour_name):
        """添加课程"""
        row = self.next_row
        self.next_row += 1
        if row>=6:
            tk.messagebox.showwarning('警告', '最多只能添加3门课程')
            self.next_row -=1
            return
        cour_entry = ctk.CTkComboBox(
            self.message_set_frame, values=self.data, state='normal', dropdown_fg_color=self.frame_fg_color,
            dropdown_hover_color=self.button_color,
            font=self.font, corner_radius=6, button_color=self.button_color
        )
        cour_entry.set(cour_name)
        cour_entry.grid(row=row, column=1, padx=6, pady=4, sticky="w")
        # 删除按钮（可选，便于移除该行）
        del_btn = ctk.CTkButton(
            self.message_set_frame, text="✖", width=20,
            fg_color="#F87171", hover_color="#EF4444",
                command=lambda: self.delete_course_row(cour_entry, del_btn, row)
        )
        del_btn.grid(row=row, column=2, padx=2, pady=4, sticky=tk.W)
        # 为这个删除按钮创建独立的 ToolTip 实例
        tip = ToolTip(del_btn, "删除该课程")
        self.dynamic_rows.append((cour_entry, del_btn, row, tip))
        # 当添加到第三门课程（row=5）时，禁用上一门课程的删除按钮并修改提示
        if row == 5 and len(self.dynamic_rows) >= 2:
            prev_entry, prev_del_btn, prev_row, prev_tip = self.dynamic_rows[-2]
            prev_del_btn.configure(state='disabled')
            prev_tip.set_text("请先删除最后一个课程")

    def delete_course_row(self, entry, del_btn, row):
        """删除指定的动态行"""
        entry.destroy()
        del_btn.destroy()
        # 从列表中移除（根据 entry 识别）
        for i, (e, d, r, tip) in enumerate(self.dynamic_rows):
            if e == entry:
                self.dynamic_rows.pop(i)
                break
        self.next_row -= 1
        # 删除后，如果 next_row 回到 5（即删除了第三门，只剩两门），恢复第二门删除按钮的可用状态及提示
        if self.next_row == 5 and len(self.dynamic_rows) >= 1:
            # 找到当前最后一门（原第二门）的删除按钮和提示
            last_entry, last_del_btn, last_row, last_tip = self.dynamic_rows[-1]
            last_del_btn.configure(state='normal')
            last_tip.set_text("删除该课程")

    def delete_record(self, file_name):
        #验证文件是否存在
        file_path = fr'task\record\《{self.dit[file_name][0].get()}》的{file_name}记录.txt'
        # 验证文件是否存在
        if os.path.exists(file_path):
            yes_no=tk.messagebox.askyesno('确认','确定要删除吗？删除后无法恢复')
            if yes_no:
                os.remove(file_path)
                tk.messagebox.showinfo('提示', f'{file_name}记录文件已成功删除')
        else:
            tk.messagebox.showwarning('警告', f'指定的{file_name}记录文件不存在')
        self.show_record(file_name)

    def delete_huancun(self):
        try:
            # 检索所有pkl文件
            folder_path = r'task/record'
            tiku_files = [f for f in os.listdir(folder_path)
                          if f.endswith('.pkl') and os.path.isfile(os.path.join(folder_path, f))]
            for tiku_file in tiku_files:
                os.remove(os.path.join(folder_path, tiku_file))
            tk.messagebox.showinfo('提示', f'缓存记录文件已成功删除')

        except:
            tk.messagebox.showwarning('警告', f'删除失败')
        self.show_question_bank()

    def prompt(self,choice):
        """提示用户"""
        if choice=='自动选择':
            tk.messagebox.showinfo('提示', '默认会从第一个未完成的作业开始刷，刷完后只会自动保存不会提交，保存后自动开始刷下一个作业')
        else:
            tk.messagebox.showinfo('提示', '到达作业页面后请手动选择您要刷的作业，刷完后只会自动保存，请确认后手动提交')

    def auto_fill_browser_driver(self, choice):
        """处理浏览器选择变化，自动填充对应的驱动路径"""
        # 清空当前驱动路径
        self.browser_driver_entry.configure(state='normal')
        self.browser_driver_entry.delete(0, tk.END)

        # 根据选择的浏览器自动填充对应的驱动路径
        if choice == "edge":
            self.browser_driver_entry.insert(0, r"edgedriver_win64\msedgedriver.exe")
        # elif choice == "chrome":
        #     self.browser_driver_entry.insert(0, r"chromedriver-win64\chromedriver-win64\chromedriver.exe")
        elif choice == "不指定浏览器":
            self.browser_driver_entry.insert(0, "无需填写")
            self.browser_driver_entry.configure(state='disabled')

    def show_user_notice(self):
        """显示用户须知弹窗"""
        # 创建顶层窗口
        notice_window = tk.Toplevel(self.root)
        notice_window.title("用户须知")
        # notice_window.geometry("500x400")
        notice_window.resizable(False, False)

        # 设置窗口模态，阻止用户操作主窗口
        notice_window.transient(self.root)
        notice_window.grab_set()

        # 将窗口置于最前端
        notice_window.wm_attributes("-topmost", True)

        # 用户须知内容
        notice_content = """欢迎使用学习通刷课程序！

    【重要声明】
    1. 本软件仅供个人学习交流使用，不得用于任何商业用途。
    2. 使用本软件产生的任何后果由使用者自行承担，开发者不承担任何责任。
    3. 请遵守学校相关规定，合理使用本软件辅助学习。
    4. 不得恶意利用本软件进行任何违规行为。
    5. 开发者保留对本软件的最终解释权。

    【使用说明】
    1. 请先在设置页面正确填写账户信息和相关配置。
    2. 建议在稳定的网络环境下使用本软件。
    3. 如遇到问题，请查看用户须知文档或联系作者。
    4. 请勿频繁使用高速倍速播放功能，以免触发平台检测机制。

    请您仔细阅读以上内容，使用本软件即表示您同意遵守上述条款。
    """

        # 创建文本框显示用户须知
        text_widget = tk.Text(notice_window, wrap=tk.WORD, font=("微软雅黑", 12),height=16,width=65)
        text_widget.insert(tk.END, notice_content)
        text_widget.config(state=tk.DISABLED)

       # 布局
        text_widget.grid(row=0, column=0,  padx=10, pady=10)

        # 创建按钮框架
        button_frame = tk.Frame(notice_window)
        button_frame.grid(row=1,column=0,pady=10)

        # 倒计时变量
        self.remaining_time = 10
        self.confirm_button = tk.Button(button_frame, text=f"确认 ({self.remaining_time}s)",width=7,height=1,font=("微软雅黑", 13),
                                        state=tk.DISABLED, command=lambda: self.close_notice(notice_window))
        self.cancel_button = tk.Button(button_frame,width=6,height=1, text="取消", command=lambda: self.exit_program(),font=("微软雅黑", 13))

        self.confirm_button.pack(side=tk.LEFT, padx=10)
        self.cancel_button.pack(side=tk.LEFT, padx=10)

        # 启动倒计时
        self.countdown(notice_window)

        # 居中显示窗口
        notice_window.update_idletasks()
        x = (notice_window.winfo_screenwidth() // 2) - (notice_window.winfo_width() // 2)
        y = (notice_window.winfo_screenheight() // 2) - (notice_window.winfo_height() // 2)
        notice_window.geometry(f"+{x}+{y}")
        # 禁止关闭窗口按钮
        notice_window.protocol("WM_DELETE_WINDOW", lambda: None)

    def countdown(self, window):
        """倒计时函数"""
        if self.remaining_time > 0:
            self.confirm_button.config(text=f"确认 ({self.remaining_time}s)")
            self.remaining_time -= 1
            window.after(1000, lambda: self.countdown(window))
        else:
            self.confirm_button.config(text="确认", state=tk.NORMAL)

    def close_notice(self, window):
        """关闭用户须知窗口"""
        window.destroy()
        self.check_update()

    def exit_program(self):
        """退出程序"""
        self.root.quit()
        self.root.destroy()
        # os._exit(0)

    def show_password(self):
        if self.password_entry.cget('show') == '*':
            self.password_entry.configure(show='')
        else:
            self.password_entry.configure(show='*')

    def show_api(self):
        if self.API_entry.cget('show') == '*':
            self.API_entry.configure(show='')
        else:
            self.API_entry.configure(show='*')

    def function_choice(self):
        if self.radio_var.get()==1 :
            self.question_label.configure(text='章节测验')
            self.question_label.grid(row=4, column=1, padx=5, pady=self.pady, sticky=tk.W)
            self.question_entry.grid(row=4, column=2, padx=5, pady=self.pady, sticky=tk.W)
            if self.question_entry.get()=='DeepSeek AI':
                self.after_finish_question.grid(row=5, column=1, padx=5, pady=self.pady, sticky=tk.W)
                self.after_finish_question_entry.grid(row=5, column=2, padx=5, pady=self.pady, sticky=tk.W)
            self.after_finish_question_entry.configure(values=["仅自动保存", '强制自动提交',
        '搜到60%的题自动提交','搜到70%的题自动提交','搜到80%的题自动提交','搜到90%的题自动提交',  '搜到100%的题自动提交'])
            self.vido_question_label.grid(row=6, column=1, padx=5, pady=self.pady, sticky=tk.W)
            self.vido_question_entry.grid(row=6, column=2, padx=5, pady=self.pady, sticky=tk.W)
            self.discussion_label.grid(row=7, column=1, padx=5, pady=self.pady, sticky=tk.W)
            self.discussion_entry.grid(row=7, column=2, padx=5, pady=self.pady, sticky=tk.W)
            self.question_entry.configure(values=['DeepSeek AI','随机答题','不刷题'])
            if self.question_entry.get()=='DeepSeek AI' or self.vido_question_entry.get()=='DeepSeek AI' or self.discussion_entry.get()=='DeepSeek AI':
                self.API_label.grid(row=8, column=1, padx=5, pady=self.pady, sticky=tk.W)
                self.API_entry.grid(row=8, column=2, padx=5, pady=self.pady, sticky=tk.W)
                self.show_api_button.grid(row=8, column=3, pady=self.pady, sticky=tk.W)
            self.speed_label.grid(row=9, column=1, padx=5, pady=self.pady, sticky=tk.W)
            self.speed_entry.grid(row=9, column=2, padx=5, pady=self.pady, sticky=tk.W)
            self.pass_face_label.grid(row=10, column=1, padx=5, pady=self.pady, sticky=tk.W)
            self.pass_face_check.grid(row=10, column=2, sticky=tk.W)
            self.lock_screen_label.grid(row=11, column=1, padx=5, pady=self.pady, sticky=tk.W)
            self.lock_screen_check.grid(row=11, column=2, sticky=tk.W)
            self.homework_label.grid_forget()
            self.homework_entry.grid_forget()

        elif self.radio_var.get()==2:
            if self.user_notice == 'True':
                self.homework_entry.set('')
            self.question_label.configure(text='作业答题')
            self.question_label.grid(row=4, column=1, padx=5, pady=self.pady, sticky=tk.W)
            self.question_entry.grid(row=4, column=2, padx=5, pady=self.pady, sticky=tk.W)
            self.question_entry.set('DeepSeek AI')
            self.question_entry.configure(values=['DeepSeek AI'])
            self.after_finish_question.grid(row=5, column=1, padx=5, pady=self.pady, sticky=tk.W)
            self.after_finish_question_entry.grid(row=5, column=2, padx=5, pady=self.pady, sticky=tk.W)
            self.after_finish_question_entry.set('仅自动保存')
            self.after_finish_question_entry.configure(values=['仅自动保存'])
            self.API_label.grid(row=7, column=1, padx=5, pady=self.pady, sticky=tk.W)
            self.API_entry.grid(row=7, column=2, padx=5, pady=self.pady, sticky=tk.W)
            self.show_api_button.grid(row=7, column=3, pady=self.pady, sticky=tk.W)
            self.homework_label.grid(row=9, column=1, padx=5, pady=self.pady, sticky=tk.W)
            self.homework_entry.grid(row=9, column=2, padx=5, pady=self.pady, sticky=tk.W)
            self.speed_label.grid_forget()
            self.speed_entry.grid_forget()
            self.lock_screen_label.grid_forget()
            self.lock_screen_check.grid_forget()
            self.vido_question_label.grid_forget()
            self.vido_question_entry.grid_forget()
            self.discussion_label.grid_forget()
            self.discussion_entry.grid_forget()
        else:
            tk.messagebox.showinfo('提示', '该功能还在开发中...,敬请期待')
            self.radio_var.set(1)
            self.function_choice()

    def shua_ti_choice(self, event):
        if self.question_entry.get() == '随机答题' and event != '视频题目' and event!='讨论':
            tk.messagebox.showinfo('提示',
                                   '请谨慎选择，只有在章节测验不计入总成绩的情况下才能使用，否则因此挂科了请自行承担后果！！！')
        if self.question_entry.get()!='DeepSeek AI':
            self.after_finish_question.grid_forget()
            self.after_finish_question_entry.grid_forget()
        else:
            self.after_finish_question.grid(row=5, column=1, padx=5, pady=self.pady, sticky=tk.W)
            self.after_finish_question_entry.grid(row=5, column=2, padx=5, pady=self.pady, sticky=tk.W)
        if self.vido_question_entry.get()=='DeepSeek AI' or self.question_entry.get()=='DeepSeek AI' or self.discussion_entry.get()=='DeepSeek AI':
            if self.vido_question_entry.get()=='DeepSeek AI' and event=='视频题目':
                tk.messagebox.showinfo('提示','这个是用于完成视频中弹出的题目，'
                                              '只有在选错答案会回退视频的情况下才建议使用DeepSeek AI，一般情况请使用随机答题,没有任何影响')
            self.API_label.grid(row=8, column=1, padx=5, pady=5, sticky=tk.W)
            self.API_entry.grid(row=8, column=2, padx=5, pady=5, sticky=tk.W)
            self.show_api_button.grid(row=8, column=3,  pady=5, sticky=tk.W)
        else:
            if self.vido_question_entry!='DeepSeek AI' and self.question_entry!='DeepSeek AI' and self.discussion_entry!='DeepSeek AI':
                self.API_label.grid_forget()
                self.API_entry.grid_forget()
                self.show_api_button.grid_forget()

    def select_frame_by_name(self, name):
        # set button color for selected button
            for i in range(len(self.button_name_list)-2):
                txt = self.button_text_list[i]
                self.button_name_list[i].configure(fg_color=self.color_value_dict.get(self.change_theme.get())[0] if name == txt else "transparent")

    def show_cloud_drive_selection(self):
        """显示网盘选择弹窗（美化版，更新内容单独区域）"""
        # 创建弹窗窗口
        selection_window = ctk.CTkToplevel(self.root)
        selection_window.iconbitmap(r'task\img\xuexitong1 .ico')
        selection_window.title("发现新版本")
        selection_window.resizable(False, False)
        selection_window.transient(self.root)
        selection_window.grab_set()
        selection_window.attributes("-topmost", True)  # 确保窗口置前

        # 设置窗口居中
        selection_window.update_idletasks()
        x = (selection_window.winfo_screenwidth() // 2) - (500 // 2)
        y = (selection_window.winfo_screenheight() // 2) - (420 // 2)
        selection_window.geometry(f"+{x}+{y}")

        # 主容器（圆角背景）
        main_frame = ctk.CTkFrame(selection_window, corner_radius=20)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 标题区域（图标+文字）
        title_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        title_frame.pack(pady=(10, 5))

        icon_label = ctk.CTkLabel(title_frame, text="✨", font=("Segoe UI Emoji", 32))
        icon_label.pack(side="left", padx=5)

        title_label = ctk.CTkLabel(title_frame,
                                   text="新版本可用",
                                   font=("Helvetica", 20, "bold"))
        title_label.pack(side="left", padx=5)

        # ========= 新增：独立的更新内容区域 =========
        update_container = ctk.CTkFrame(main_frame, corner_radius=12, fg_color="#f0f0f0",height=10)  # 浅灰底色
        update_container.pack(pady=(5, 10), padx=10, fill="x")

        # 区域标题（带小图标）
        update_title_frame = ctk.CTkFrame(update_container, fg_color="transparent")
        update_title_frame.pack(anchor="w", padx=12, pady=(8, 0))

        update_icon = ctk.CTkLabel(update_title_frame, text="📦", font=("Segoe UI Emoji", 14))
        update_icon.pack(side="left", padx=(0, 5))

        update_title_label = ctk.CTkLabel(update_title_frame,
                                          text="更新内容",
                                          font=("Helvetica", 13, "bold"),
                                          text_color="#333333")
        update_title_label.pack(side="left")

        # 删除 update_scroll_frame，直接使用普通 Frame
        update_content_frame = ctk.CTkFrame(update_container, fg_color="transparent")
        update_content_frame.pack(fill="x", padx=10, pady=(5,0))

        update_content_label =  ctk.CTkTextbox(update_content_frame, height=110, width=197,fg_color='transparent')
        update_content_label.insert(tk.END,self.updata_concent)
        update_content_label.pack(fill="x", padx=5, pady=2)


        # ========= 区域2：网盘选择卡片（独立区域） =========
        drive_container = ctk.CTkFrame(main_frame, corner_radius=12, fg_color="#f0f0f0")
        drive_container.pack(pady=(0, 10), padx=10, fill="x")

        # 区域标题（带小图标）
        drive_title_frame = ctk.CTkFrame(drive_container, fg_color="transparent")
        drive_title_frame.pack(anchor="w", padx=12, pady=(8, 5))

        drive_icon = ctk.CTkLabel(drive_title_frame, text="☁️", font=("Segoe UI Emoji", 14))
        drive_icon.pack(side="left", padx=(0, 5))

        drive_title_label = ctk.CTkLabel(drive_title_frame,
                                         text="选择下载方式",
                                         font=("Helvetica", 13, "bold"),
                                         text_color="#333333")
        drive_title_label.pack(side="left")

        # 提示信息（移入网盘区域内）
        info_label = ctk.CTkLabel(drive_container,
                                  text="建议使用推荐渠道以获得更快的速度",
                                  font=("Helvetica", 11),
                                  text_color="#666666",
                                  wraplength=440,
                                  justify="center")
        info_label.pack(pady=(0, 8), padx=10)

        # 网盘按钮列表（原 drive_frame 内容）
        cloud_drives = [
            {
                "name": "⚡ 迅雷网盘",
                "url": "https://pan.xunlei.com/s/VO_FdZ-t7lDMpGFgLcuH81DTA1?pwd=viah#",
                "description": "推荐 ·支持迅雷加速下载",
                "color": "#00A8FF",
                "hover": "#33B9FF"
            },
            {
                "name": "☁️ 夸克网盘",
                "url": "https://pan.quark.cn/s/eba634db1544",
                "description": " 下载速度快",
                "color": "#FF6B35",
                "hover": "#FF8555"
            },
            {
                "name": "🐻 百度网盘",
                "url": "https://pan.baidu.com/s/1vFpIWyRyX4CW-9j1pdvEpw?pwd=1234",
                "description": "提取码: 1234",
                "color": "#4CD964",
                "hover": "#6DE07E"
            }
        ]

        # 内部按钮容器（垂直排列）
        buttons_frame = ctk.CTkFrame(drive_container, fg_color="transparent")
        buttons_frame.pack(pady=(0, 12), padx=10, fill="x")

        for drive in cloud_drives:
            btn_container = ctk.CTkFrame(buttons_frame, fg_color="transparent")
            btn_container.pack(pady=6, fill="x")

            drive_button = ctk.CTkButton(
                btn_container,
                text=f"{drive['name']}\n{drive['description']}",
                font=("Helvetica", 13, "bold"),
                fg_color=drive['color'],
                hover_color=drive['hover'],
                text_color="white",
                corner_radius=12,
                height=70,
                border_width=0,
                anchor="center"
            )
            drive_button.pack(fill="x")
            drive_button.configure(command=lambda url=drive['url']: self.open_cloud_drive(url, selection_window))

        # ========= 底部操作栏 =========
        separator = ctk.CTkFrame(main_frame, height=2, fg_color="gray70")
        separator.pack(fill="x", pady=(10, 10), padx=30)

        bottom_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        bottom_frame.pack(pady=(0, 10))

        skip_button = ctk.CTkButton(
            bottom_frame,
            text="跳过此次更新",
            font=("Helvetica", 12),
            fg_color="transparent",
            hover_color="#E0E0E0",
            text_color="gray",
            border_width=2,
            border_color="gray",
            corner_radius=8,
            width=140,
            height=32
        )
        skip_button.pack(side="left", padx=10)
        skip_button.configure(command=selection_window.destroy)

        reminder_label = ctk.CTkLabel(
            bottom_frame,
            text="后续可在「主页」中再次检查更新",
            font=("Helvetica", 10),
            text_color="gray"
        )
        reminder_label.pack(side="right", padx=10)

        # 键盘绑定（回车默认选择第一个网盘）
        selection_window.bind('<Return>', lambda e: self.open_cloud_drive(cloud_drives[0]['url'], selection_window))
        selection_window.bind('<Escape>', lambda e: selection_window.destroy())

    def open_cloud_drive(self, url, window=None):
        """打开选择的网盘链接"""
        try:
            import webbrowser
            webbrowser.open(url)

            # 显示成功消息
            tk.messagebox.showinfo("成功", f"已打开浏览器访问网盘链接\n链接已复制到剪贴板")

            # 复制链接到剪贴板
            self.root.clipboard_clear()
            self.root.clipboard_append(url)

            # 关闭选择窗口
            if window:
                window.destroy()

        except Exception as e:
            tk.messagebox.showerror("错误", f"打开浏览器失败：{str(e)}")

    def check_update(self):
        self.text_box.configure(state=tk.NORMAL)
        # 清空文本框内容
        # self.text_box.delete('1.0', tk.END)
        # 获取最新的Release信息
        release_url = r'https://api.github.com/repos/Mortal004/Xuexitong_shuake/releases/latest'
        try:
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.3",
                "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
                "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
                "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.96 Safari/537.36"
            ]
            headers = {
                "User-Agent": random.choice(user_agents)
            }
            response = requests.get(release_url, headers=headers)
            if response.status_code == 200:
                release_info = response.json()
                self.updata_concent=release_info['body']
                assets = release_info.get('assets', [])
                if assets:
                    # self.text_box.insert(tk.END, '连接成功\n')
                    # 获取第一个文件（假设是我们要下载的文件夹压缩包）
                    first_asset = assets[0]
                    download_url = first_asset['browser_download_url']
                    file_name = first_asset['name']
                    created_time=first_asset['created_at']

                    # 读取当前版本信息
                    with open('task/tool/version_info', 'r') as f:
                        version = f.read()

                    if version in file_name:
                        self.text_box.insert(tk.END, '\n当前版本为最新版本，无需更新！')
                        logger.info(f'当前版本为{version}，与最新版本{file_name}相同，无需更新！')
                    else:
                        self.text_box.insert(tk.END, '\n检测到有新版本可用')
                        logger.info(f'当前版本为{version}，与最新版本{file_name}不同，需要更新！')

                        # 创建网盘选择弹窗
                        self.show_cloud_drive_selection()
        except Exception as e:
            self.text_box.insert(tk.END, '\n检查更新失败，请检查网络连接！')
            logger.error(f'检查更新失败：{e}')
            # self.text_box.insert(tk.END, f'错误信息：{e}\n')

    def toggle_topmost(self):
        """切换窗口始终置顶属性"""
        if self.topmost_check.get():
            self.is_topmost = False
            self.root.wm_attributes("-topmost", True)
        else:
            self.is_topmost = True
            self.root.wm_attributes("-topmost", False)

    def show_frame(self, frame):
        for f in self.frame_name_list[:8]:
            if f != frame:
                f.grid_forget()
            else:
                f.grid(row=1, column=1,sticky='nsew')

    def show_main(self):
        self.select_frame_by_name('主页')
        self.show_frame(self.main_frame)

    def show_record(self, name):
        self.select_frame_by_name(self.dit[name][1])
        self.dit[name][2].configure(state=tk.NORMAL)
        self.dit[name][2].delete('1.0', tk.END)
        try:
            with open(fr'task\record\《{self.dit[name][0].get()}》的{name}记录.txt', 'r', encoding='utf-8') as f:
                content = f.read()
                self.dit[name][2].insert(tk.END, content)
        except FileNotFoundError:
            self.dit[name][2].insert(tk.END, f'暂未查询到《{self.dit[name][0].get()}》的{name}记录')
        self.show_frame(self.dit[name][3])
        self.dit[name][2].configure(state=tk.DISABLED)

    def show_question_bank(self,*key):
        self.select_frame_by_name('题库查询')
        self.tiku_text.configure(state=tk.NORMAL)
        self.tiku_text.delete('1.0', tk.END)
        try:
            # 检索所有pkl文件
            folder_path = r'task/record'
            tiku_files = [f for f in os.listdir(folder_path)
                          if f.endswith('.pkl') and os.path.isfile(os.path.join(folder_path, f))]
            tiku_txt = ''
            for tiku_file in tiku_files:
                if 'ques1' not in tiku_file:
                    continue
                tiku_file_path = os.path.join(folder_path, tiku_file)
                tiku_txt += "问题:  " + pickle.load(open(tiku_file_path, 'rb'))['value']['question'] + '\n'
                tiku_txt += str(pickle.load(open(tiku_file_path, 'rb'))['value']['options']) + '\n'
                tiku_txt += '答案为：' + str(pickle.load(open(tiku_file_path, 'rb'))['value']['answer']) + '\n\n'
            if tiku_txt == '':
                self.tiku_text.insert( tk.END,'暂无缓存的题目')
            self.tiku_text.insert(tk.END, tiku_txt)
        except FileNotFoundError:
            self.tiku_text.insert(tk.END,'暂无缓存的题目')
        self.show_frame(self.question_bank_frame)
        self.tiku_text.configure(state=tk.DISABLED)

    def show_error(self):
        self.select_frame_by_name('报错日志')
        try:
            self.error_text.configure(state=tk.NORMAL)
            with open('error.log', 'r',encoding='utf-8') as f:
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

    def select_file(self):
        file_path = filedialog.askopenfilename(title="选择文件", filetypes=[("", "*.exe")])
        if file_path:
            self.browser_driver_entry.delete(0, tk.END)
            self.browser_driver_entry.insert(tk.END,file_path)

    def start_button_normal(self):
        time.sleep(5)
        self.start_button.configure(state=tk.NORMAL)

    def run_program(self,file_name):
        self.fold_frame()
        """
        运行 main.py 程序，并将其输出实时显示在 GUI 的文本框中。
        """
        # 确保文本框可编辑
        self.text_box.configure(state=tk.NORMAL)
        # 清空文本框内容
        self.text_box.delete('1.0', tk.END)
        def read_output():
            """
            读取 main.py 程序的输出，并将其显示在文本框中。
            """
            # 启动 main.py 程序
            self.process = subprocess.Popen(file_name,
                                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            color_tag = None
            logger.info('======================主程序开始运行======================')
            while True:
                output = self.process.stdout.readline()
                if self.process is None:
                    break
                if output == b'' and self.process.poll() is not None:
                    break
                if output:
                    try:
                        decoded_output = output.decode()
                    except UnicodeDecodeError:
                        decoded_output = output.decode('gbk', errors='ignore')
                    # 处理 [91m 这种颜色标记
                    ansi_color_start = re.search(r'\[(\d+?)m', decoded_output)
                    ansi_color_end = re.search(r'\[0m', decoded_output)
                    if ansi_color_start:
                        ansi_color_code = ansi_color_start.group(1)
                        if ansi_color_code == '91':
                            color_tag = 'red'
                            self.text_box.tag_config(color_tag, foreground=color_tag)
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
                            self.text_box.tag_config(color_tag, foreground=color_tag)
                            decoded_output = decoded_output.replace(color_start.group(0), "")
                        if color_end:
                            color_tag = None
                            decoded_output = decoded_output.replace(color_end.group(0), "")
                    decoded_output = decoded_output.replace('', '')
                    if color_tag:
                        self.text_box.insert(tk.END, decoded_output, color_tag)
                    else:
                        self.text_box.insert(tk.END, decoded_output)
                    decoded_output=re.sub(r'[\n\t\r]', '', decoded_output)
                    if decoded_output.strip():
                        logger.info(decoded_output)
                    if '❌' in decoded_output:
                        self.close()
                    self.text_box.see(tk.END)  # 自动滚动到文本框底部，以显示最新内容
            self.process.stdout.close()
            try:
                self.process.wait()
            except:
                pass
            self.text_box.configure(state=tk.DISABLED)

        # 使用线程来运行读取输出的函数，避免阻塞主事件循环
        self.thread = threading.Thread(target=read_output)
        self.thread.start()


    def start(self):
        self.process_condition=True
        self.close_button.grid(row=0, column=0, padx=5, pady=10)
        self.start_button.grid_forget()
        with open(r'task/tool/account_info.json', 'r', encoding='utf-8') as fil:
            self.account_info = json.load(fil)
            if self.account_info['phone_number'] == '':
                tk.messagebox.showerror('警告', message='请在设置页面填写相关信息再保存，如果已经保存，请在关闭主窗口后，'
                                                        '再右键点击刷课程序用管理员权限运行,进入设置页面填写相关信息')
                return
            file_name = self.account_info['file_name']
        threading.Thread(target=self.run_program,args=(file_name,)).start()
        threading.Thread(target=self.start_button_normal).start()

    def open_timer_window(self):
        """打开定时刷课设置窗口"""
        timer_window = ctk.CTkToplevel(self.root)
        timer_window.title("⏰ 定时刷课设置")
        timer_window.geometry("350x200")
        timer_window.resizable(False, False)
        timer_window.transient(self.root)
        timer_window.grab_set()
        # 开始时间设置
        ctk.CTkLabel(timer_window, text="开始时间 (HH:MM:SS):", font=self.font).grid(row=0, column=0, padx=10, pady=10,
                                                                                     sticky="w")
        self.start_time_entry = ctk.CTkEntry(timer_window, width=120, font=self.font)
        self.start_time_entry.grid(row=0, column=1, padx=10, pady=10)
        self.start_time_entry.insert(0, self.timer_start_time)
        # 结束时间设置
        ctk.CTkLabel(timer_window, text="结束时间 (HH:MM:SS):", font=self.font).grid(row=1, column=0, padx=10, pady=10,
                                                                                     sticky="w")
        self.end_time_entry = ctk.CTkEntry(timer_window, width=120, font=self.font)
        self.end_time_entry.grid(row=1, column=1, padx=10, pady=10)
        self.end_time_entry.insert(0, self.timer_end_time)
        # 确认按钮
        confirm_btn = ctk.CTkButton(timer_window, text="开启定时", fg_color=self.button_color,
                                    hover_color=self.button_hover_color, font=self.font,
                                    command=lambda: self.set_timer(timer_window))
        confirm_btn.grid(row=2, column=0,  padx=10, pady=20)
        #取消定时
        cancel_btn = ctk.CTkButton(timer_window, text="禁用定时", fg_color=self.button_color,hover_color=self.button_hover_color,font=self.font,
                                    command=lambda: self.close_timer_window(timer_window))
        cancel_btn.grid(row=2, column=1, padx=10, pady=20)

    def set_timer(self, window):
        """设置定时刷课时间"""
        start_time_str = self.start_time_entry.get().strip()
        end_time_str = self.end_time_entry.get().strip()
        # 验证时间格式
        time_pattern = r"^([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$"
        if not re.match(time_pattern, start_time_str):
            tk.messagebox.showerror("错误", "开始时间格式不正确，请输入 HH:MM:SS 格式")
            return
        if not re.match(time_pattern, end_time_str):
            tk.messagebox.showerror("错误", "结束时间格式不正确，请输入 HH:MM:SS 格式")
            return
        # 验证结束时间大于开始时间
        start_h, start_m, start_s = map(int, start_time_str.split(":"))
        end_h, end_m, end_s = map(int, end_time_str.split(":"))
        start_total = start_h * 3600 + start_m * 60 + start_s
        end_total = end_h * 3600 + end_m * 60 + end_s
        if start_total==end_total:
            tk.messagebox.showerror("错误", "结束时间不能与开始时间相同")
            return

        self.timer_start_time = start_time_str
        self.timer_end_time = end_time_str
        self.timer_active = True
        self.text_box.configure(state=tk.NORMAL)
        self.text_box.insert(tk.END,
                             f"\n定时刷课已开启:\n  开始时间: {self.timer_start_time}\n  结束时间: {self.timer_end_time}"
                             f"\n请勿关闭此窗口，否则定时刷课将无法正常开启")

        self.text_box.see(tk.END)
        with open(r'task/tool/account_info.json', 'r', encoding='utf-8') as f:
            self.account_info = json.load(f)
        self.account_info['timer_active']='True'
        self.account_info['timer_start']=self.timer_start_time
        self.account_info['timer_end']=self.timer_end_time
        with open(r'task/tool/account_info.json', 'w', encoding='utf-8') as f:
            json.dump(self.account_info, f)
        window.destroy()

    # 关闭定时刷课设置窗口
    def close_timer_window(self, window):
        """关闭定时刷课设置窗口"""
        window.destroy()
        self.timer_active = False
        self.text_box.configure(state=tk.NORMAL)
        self.text_box.insert(tk.END, "\n定时刷课已禁用")
        with open(r'task/tool/account_info.json', 'r', encoding='utf-8') as f:
            self.account_info = json.load(f)
        self.account_info['timer_active']='False'
        with open(r'task/tool/account_info.json', 'w', encoding='utf-8') as f:
            json.dump(self.account_info, f)
    def close(self):

        self.process_condition=False
        self.start_button.grid(row=0, column=0,padx=5,  pady=10)
        self.close_button.grid_forget()
        self.reopen_frame()
        if self.process is not None:
            try:
                if os.name == 'nt':  # Windows 平台
                    subprocess.run(['taskkill', '/F', '/T', '/PID', str(self.process.pid)])
                else:  # Unix 平台
                    os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                self.text_box.insert(tk.END, "程序已成功关闭\n")
                logger.info('======================程序已成功关闭======================')
            except Exception as e:
                self.text_box.insert(tk.END, f"关闭失败: {e}\n")
                logger.error(f"======================程序关闭失败: {e}======================")
            finally:
                self.process = None

    # 每秒更新 GUI 中的时间显示
    def update_time(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.configure(text=f"当前时间: {current_time}")
        self.root.after(1000, self.update_time)  # 每秒更新一次
        if self.timer_start_time in current_time and not self.process_condition and self.timer_active:
            self.start()
        if self.timer_end_time in current_time and self.process_condition and self.timer_active:
            self.close()

    def change_font(self):
        self.font = (self.font_entry.get(), int(self.size_entry.get()))
        self.style.configure('TLabelframe.Label',font=self.font)

        def update_font(widget):
            if isinstance(widget,( tk.Label, tk.Button, tk.Text,ttk.Label, tk.Entry, tk.LabelFrame)):
                widget.config(font=self.font)
            elif isinstance(widget,ttk.Checkbutton):
                style=ttk.Style()
                style.configure('TCheckbutton',font=self.font)
                widget.config(style='TCheckbutton')
            for child in widget.winfo_children():
                update_font(child)

        update_font(self.root)

    def save_course(self):
            data = []
            try:
                with open(r'task/tool/course_name.json', 'r') as f:
                    dit = json.load(f)
                    data=dit.get(self.phone_number_entry.get(),[])
            except FileNotFoundError:
                pass
            for content in self.all_courses:
                if content not in data:
                    data.append(content)
            with open(r'task/tool/course_name.json', 'w' , encoding='utf-8')as f:
                dit[self.phone_number_entry.get()]=data
                json.dump(dit, f)

    def save(self):
        try:
            with open(r'task/tool/account_info.json', 'r', encoding='utf-8') as f:
                self.account_info = json.load(f)
        except FileNotFoundError:
            self.account_info = {}
        self.account_info['user_notice']='False'
        if self.browser_entry.get()=='':
            tk.messagebox.showerror('警告', message='请选择浏览器')
            return False
        else:
            self.account_info['browser']=self.browser_entry.get()
        if self.browser_driver_entry.get()=='':
            tk.messagebox.showerror('警告', message='请填写驱动的地址')
            return False
        else:
            self.account_info['driver_path']=self.browser_driver_entry.get()
        if self.browser_entry.get()!='不指定浏览器':
            if self.browser_entry.get() not in self.browser_driver_entry.get():
                tk.messagebox.showerror('警告', message='请检查你的浏览器是否与驱动对应')
                return False
        else:
            self.account_info['driver_path']=''
        if self.phone_number_entry.get()=='':
            tk.messagebox.showerror('警告', message='请填写手机号')
            return False
        else:
            self.account_info['phone_number'] = self.phone_number_entry.get().replace('\n','')
        if  self.password_entry.get()=='':
            tk.messagebox.showerror('警告', message='请填写密码')
            return False
        else:
            self.account_info['password'] = self.password_entry.get().replace('\n','')
        if self.cour_entry.get()=='':
            tk.messagebox.showerror('警告', message='请填写课程名称')
            return False
        else:
            courses=[self.cour_entry.get().replace('\n', '')]
            add_courses = [entry.get() for entry, _, _,_ in self.dynamic_rows if entry.get().replace('\n', '')]
            self.all_courses = courses+add_courses
            self.account_info['cour'] = self.all_courses
        if self.question_entry.get() ==''  :
            tk.messagebox.showerror('警告', message='请完成章节测验刷题设置')
            return False
        else:
            self.account_info['choice'] = self.question_entry.get()
        if self.after_finish_question_entry.get()== '' and self.question_entry.get()=='DeepSeek AI':
            tk.messagebox.showerror('警告', message='请完成答完题后的设置')
            return False
        else:
            self.account_info['after_finish_question'] = self.after_finish_question_entry.get()
        if self.vido_question_entry.get() =='' and self.radio_var.get()==1 :
            tk.messagebox.showerror('警告', message='请完成视频题目设置')
            return False
        else:
            self.account_info['video_title_choice'] = self.vido_question_entry.get()
        if self.discussion_entry.get() ==''  and self.radio_var.get()==1:
            tk.messagebox.showerror('警告', message='请完成讨论设置')
            return False
        else:
            self.account_info['discussion_choice'] = self.discussion_entry.get()
        if self.question_entry.get() == 'DeepSeek AI' or self.vido_question_entry.get() == 'DeepSeek AI' or self.discussion_entry.get() == 'DeepSeek AI':
            if self.API_entry.get()=='':
                tk.messagebox.showerror('警告', message='请填写API密钥')
                return False
            else:
                self.account_info['API'] = self.API_entry.get()
        if self.speed_entry.get()==''and self.radio_var.get()==1:
            tk.messagebox.showerror('警告', message='请填写倍数')
            return False
        else:
            self.account_info['speed']=self.speed_entry.get()
        if self.homework_entry.get() == '' and self.radio_var.get() == 2:
            tk.messagebox.showerror('警告', message='请填写作业选择形式')
            return False
        else:
            self.account_info['homework'] = self.homework_entry.get()
        if self.radio_var.get()==1:
            self.account_info['task_type']='章节'
        elif self.radio_var.get()==2:
            self.account_info['task_type']='作业'
        self.account_info['font_type'] = self.font_entry.get()
        self.account_info['font_size'] = self.size_entry.get()
        self.account_info['pass_face'] = self.pass_face_check.get()
        self.account_info['lock_screen'] = self.lock_screen_check.get()
        self.account_info['radio_var']=self.radio_var.get()

        result = tk.messagebox.askokcancel('确认保存', '你确定要保存吗？\n(使用DeepSeek可支持全题型作答)')
        if result:
            with open(r'task/tool/account_info.json', 'w', encoding='utf-8') as f:
                json.dump(self.account_info, f)
            with open(r'task/tool/account_info.json', 'r', encoding='utf-8') as fil:
                self.account_info = json.load(fil)
                if self.account_info['phone_number']!='':
                    tk.messagebox.showinfo('', '保存成功')
                else:
                    tk.messagebox.showerror('警告', message='保存失败，请在关闭主窗口后，再右键点击刷课程序用管理员权限打开')

            self.save_course()
            self.change_font()
            self.root.update()

    def load_data(self):
        try:

            with open(r'task/tool/account_info.json', 'r', encoding='utf-8') as fil:
                self.account_info = json.load(fil)
                with open(r'task/tool/course_name.json', 'r') as f:
                    dit = json.load(f)
                    self.data=dit.get(self.account_info['phone_number'],[])
                    if self.data:
                        self.course_score_entry.configure(values= tuple(self.data))
                        self.course_vido_entry.configure(values= tuple(self.data))
                        self.cour_entry.configure(values=tuple(self.data))
                self.user_notice=self.account_info['user_notice']
                self.course_score_entry.set( self.account_info['cour'][0])
                self.course_vido_entry.set( self.account_info['cour'][0])
                self.browser_entry.set( self.account_info['browser'])
                if self.account_info['browser']!='不指定浏览器':
                    self.browser_driver_entry.insert(0, self.account_info['driver_path'])
                else:
                    self.browser_driver_entry.insert(0, '无需填写')
                    self.browser_driver_entry.configure(state=tk.DISABLED)
                self.speed_entry.set( self.account_info['speed'])
                self.phone_number_entry.insert( 0,self.account_info['phone_number'])
                self.password_entry.insert(0, self.account_info['password'])
                self.cour_entry.set( self.account_info['cour'][0])
                self.question_entry.set( self.account_info['choice'])
                self.after_finish_question_entry.set( self.account_info['after_finish_question'])
                if self.account_info['video_title_choice']!='':
                    self.vido_question_entry.set( self.account_info['video_title_choice'])
                self.discussion_entry.set( self.account_info['discussion_choice'])
                self.homework_entry.set( self.account_info['homework'])
                self.radio_var.set(self.account_info['radio_var'])
                if self.account_info['pass_face']==0:
                    self.pass_face_check.deselect()
                else:
                    self.pass_face_check.select()
                if self.account_info['lock_screen']==0:
                    self.lock_screen_check.deselect()
                else:
                    self.lock_screen_check.select()
                try:
                    self.API_entry.insert(0, self.account_info['API'])
                    self.font_entry.set(self.account_info['font_type'])
                    self.size_entry.set(self.account_info['font_size'])
                    self.change_font()
                except:
                    pass
                for cour_name in self.account_info['cour'][1:]:
                    self.add_course(cour_name)
                if self.account_info['timer_active']=='True':
                    self.timer_active=True
                self.timer_start_time=self.account_info['timer_start']
                self.timer_end_time=self.account_info['timer_end']
        except FileNotFoundError:
            pass

    def fold_frame(self):
        self.navigation_frame.grid_forget()
        self.open_frame.grid(row=0, column=0,rowspan=2, sticky="ns")

    def reopen_frame(self):
        self.open_frame.grid_forget()
        self.navigation_frame.grid(row=0, column=0, rowspan=2,sticky="nsew")

    def change_appearance_mode_event(self, theme):
        colors = self.color_value_dict.get(theme, ['#1E88E5', '#F8FAFC', '#90CAF9'])

        self.record_color_lst.append(theme)
        for frame in self.frame_name_list:
            frame.configure(fg_color=self.color_value_dict.get(theme)[1])
        self.navigation_frame.configure(fg_color=self.color_value_dict.get(theme)[2])
        self.style.configure('TLabelframe', background=self.color_value_dict.get(theme)[1])
        self.style.configure('TLabelframe.Label', background=self.color_value_dict.get(theme)[1])
        self.style.configure('TLabel',background=self.color_value_dict.get(theme)[1])
        for check in self.check_switch:
            check.configure(bg_color=colors[1], progress_color=colors[0])
        for button in self.button_name_list1:
            button.configure(fg_color=self.color_value_dict.get(theme)[0],hover_color=self.color_value_dict.get(theme)[2])
        for combox in self.combobox_lst:
            combox.configure(dropdown_fg_color=self.color_value_dict.get(theme)[1],dropdown_hover_color=self.color_value_dict.get(theme)[0],bg_color='transparent',
                             button_color=self.color_value_dict.get(theme)[0],button_hover_color=self.color_value_dict.get(theme)[2])
        for i in range(len(self.button_name_list)):
            if self.button_name_list[i].cget('fg_color')==self.color_value_dict.get(self.record_color_lst[len(self.record_color_lst)-2])[0]:
                self.button_name_list[i].configure(fg_color=self.color_value_dict.get(theme)[0])
            self.button_name_list[i].configure(hover_color=self.color_value_dict.get(theme)[0])

    def hint(self,speed):
        if int(speed)>2:
            tk.messagebox.showinfo('提示','倍数过高，已完成的任务点可能会被清空，请谨慎使用')
        else:
            pass


if __name__ == "__main__":
    start = Start()
    start.root.mainloop()

