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
import shutil
import customtkinter as ctk


class Start:
    def __init__(self):

        self.result = None
        self.colorama_to_tkinter = {
            'RED': 'red',
            'YELLOW': 'yellow',
            'BLUE': 'blue',
            'GREEN': 'green',
            'MAGENTA': 'magenta'
        }
        self.process = None
        self.font = ("Helvetica", 13)
        self.cour = None
        self.password = None
        self.phone_number = None
        self.account_info = None
        self.frame_fg_color = "#E3F2FD"
        self.button_color = "#1F6AA5"
        self.button_hover_color='#81AED1'
        self.color_value_dict={'blue':['#1F6AA5','#E3F2FD','#81AED1'],
                                'green':['#2CC985','#E8F5E9','#8ADFB7'],
                                "red": ["#FF3333", "#FF9999", "#FF6666"],
                                "gray": ["#666666", "#CCCCCC", "#999999"],
                                'sky-lake':["#3399CC","#CCFFFF","#7FCCE5"],
                               'deep-light':["#115577","#DDFFFF","#77AABB"],
                               'blue-light':['#4488BB','#EEEEFF',"#99BBDD"]}# 颜色值字典[深，浅,中]
        self.record_color_lst= ['blue']
        self.root = ctk.CTk()
        ctk.set_appearance_mode("light")

        self.root.geometry("+1290+20")  # 设置窗口大小
        self.root.title('学习通刷课')
        # 初始设定窗口置顶
        self.is_topmost = True
        self.root.wm_attributes("-topmost", self.is_topmost)
        self.main_frame =  ctk.CTkFrame(self.root,fg_color=self.frame_fg_color,corner_radius=0)
        self.set_frame =  ctk.CTkFrame(self.root,fg_color=self.frame_fg_color,corner_radius=0)
        self.help_frame =  ctk.CTkFrame(self.root,fg_color=self.frame_fg_color,corner_radius=0)
        self.vido_frame =  ctk.CTkFrame(self.root,fg_color=self.frame_fg_color,corner_radius=0)
        self.score_frame = ctk.CTkFrame(self.root,fg_color=self.frame_fg_color,corner_radius=0)
        self.error_frame=  ctk.CTkFrame(self.root,fg_color=self.frame_fg_color,corner_radius=0)
        self.money_frame =  ctk.CTkFrame(self.root,fg_color=self.frame_fg_color,corner_radius=0)
        self.root.resizable(False, False)  # 禁止用户调整窗口大小
         # 使用ico格式的图标文件
        self.root.iconbitmap(r'task\img\xuexitong1 .ico')
        #透明度
        self.root.attributes('-alpha',1)
        #加载图片
        self.menu_image = ctk.CTkImage(light_image=Image.open(r"task\img\menu.png"), size=(30, 30))
        self.fold_image = ctk.CTkImage(light_image=Image.open(r"task\img\fold.png"), size=(15, 30))
        self.open_image = ctk.CTkImage(light_image=Image.open(r"task\img\open.png"), size=(15, 30))
        self.image_name_list = ['home_dark.png','set.png','help.png','vido.png','score.png','error.png','give_money.png']
        self.image_list = ['home_image','set_image','help_image','vido_image','score_image','error_image','money_image']
        for i in range(len(self.image_name_list)):
            self.image_list[i] = ctk.CTkImage(light_image=Image.open(r"task\img\{}".format(self.image_name_list[i])), size=(20, 20))

        # ----------------创建菜单页面----------------
        self.navigation_frame = ctk.CTkFrame(self.root, corner_radius=0,fg_color=self.frame_fg_color)
        self.navigation_frame.grid(row=0, column=0,rowspan=2, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(9, weight=1)
        #----------------展开页面----------------
        self.open_frame= ctk.CTkFrame(self.root, corner_radius=0,width=10,fg_color=self.frame_fg_color)
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
        self.fold_button.grid(row=8, column=0, sticky="ew")
        self.button_text_list = ["主页","设置","帮助","刷课日志","测试成绩","报错日志","赞助作者"]
        self.button_command_list = [self.show_main,self.show_set,self.show_help,self.show_vido,self.show_score,self.show_error,self.show_money]
        self.button_name_list = ['home_button','set_button','help_button','vido_button','score_button','error_button','money_button',self.open_button,self.fold_button]
        for i in range(len(self.button_text_list)):
            self.button_name_list[i] = ctk.CTkButton(self.navigation_frame, corner_radius=0,width=10,height=40, border_spacing=10,
                                                   text=self.button_text_list[i],font=self.font,image=self.image_list[i],
                                                   fg_color="transparent", text_color='black',
                                                   hover_color=self.button_color, anchor="w",
                                                    command=self.button_command_list[i])
            self.button_name_list[i].grid(row=i+1, column=0, sticky="ew")
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
                              self.score_frame,self.error_frame,self.money_frame,
                              self.open_frame,self.navigation_frame,self.label_frame]
        #  当前时间显示
        self.time_label = ctk.CTkLabel(self.label_frame, text="", fg_color='transparent', font=self.font)
        self.time_label.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)
        #声明
        self.copyright_label = ctk.CTkLabel(self.label_frame,font=self.font,
                                            text="声明：该脚本仅用于托管完成学习通的课程，不可用作商用\n(在电脑上开启脚本后不需要人为监管，可自动看视频和完成题目)\n", fg_color='transparent')
        self.copyright_label.grid(row=1, column=0, columnspan=2, sticky=tk.W+tk.E)

        # ---------------- 主页 ----------------
        # 启动程序按钮
        self.start_button = ctk.CTkButton(self.main_frame, text="启动程序",height=40, border_spacing=10,fg_color=self.button_color,
                                          command=lambda: self.run_program(['python','main.py']), font=self.font,hover_color=self.button_hover_color)
        # self.button1.config(image=self.img)
        self.start_button.grid(row=0, column=0,padx=5, pady=10)
        # 关闭程序按钮
        self.close_button = ctk.CTkButton(self.main_frame, text="关闭程序",height=40, border_spacing=10,fg_color=self.button_color,
                                          command=self.close,font=self.font,hover_color=self.button_hover_color)
        self.close_button.grid(row=0, column=1,padx=5,  pady=10)
        #更新
        self.update_button = ctk.CTkButton(self.main_frame, text="检查更新",height=40, border_spacing=10,fg_color=self.button_color,
                                           command=self.check_update,font=self.font,hover_color=self.button_hover_color)
        self.update_button.grid(row=0, column=2,padx=5,  pady=10)
        # 创建只读文本框#202022
        self.text_box = ctk.CTkTextbox(self.main_frame,
                                       fg_color='transparent',
                                       height=24 * 20,  # CTkTextbox 使用像素单位
                                       width=20 * 10,  # 需要根据字符宽度估算
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
        # 创建标签
        self.progress_label = ctk.CTkLabel(self.main_frame, text="当前进度：0.0%", font=self.font,
                                           fg_color='transparent')
        # 创建进度条
        self.progress_bar = ctk.CTkProgressBar(self.main_frame, width=250, height=20)
        # ---------------- 刷课记录 ----------------
        # 下拉选项框（包含可输入部分）
        self.course_vido_entry = ctk.CTkComboBox(self.vido_frame,dropdown_font=self.font,values=[],
                                                 dropdown_fg_color=self.frame_fg_color,
                                                 button_color=self.button_color,
                                                 button_hover_color=self.button_hover_color,
                                                 dropdown_hover_color=self.button_color,
                                                 font=self.font,command=self.show_vido)
        self.course_vido_entry['state'] = 'normal'
        self.course_name = self.course_vido_entry.get()
        self.course_vido_entry.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W + tk.E)  # 使用 sticky 参数使组件填满整个单元格
        # 按钮
        self.button1 = ctk.CTkButton(self.vido_frame, text="查询", command=self.show_vido,fg_color=self.button_color,
                                     font=self.font,hover_color=self.button_hover_color)
        self.button1.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)  # 使用 sticky 参数使组件填满整个单元格
        # 配置按钮框架的列权重，使按钮居中
        self.score_frame.rowconfigure(0, weight=1)
        # self.score_frame.columnconfigure(1, weight=1)
        #创建只读文本框
        self.vido_text = ctk.CTkTextbox(self.vido_frame, height=527, width=435,font=self.font,fg_color='transparent')
        self.vido_text.configure(state=tk.DISABLED)
        self.vido_text.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky=tk.W+tk.E+tk.N+tk.S)

        # ---------------- 成绩日志 ----------------
        # 下拉选项框（包含可输入部分）
        self.course_score_entry = ctk.CTkComboBox(self.score_frame,dropdown_font=self.font,font=self.font,values=[],
                                                  dropdown_fg_color=self.frame_fg_color,
                                                  button_color=self.button_color,
                                                  button_hover_color=self.button_hover_color,
                                                  dropdown_hover_color=self.button_color,
                                                  command=self.show_score)
        # self.course_score_entry['state'] = 'normal'
        self.course_name=self.course_score_entry.get()
        self.course_score_entry.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W+tk.E)  # 使用 sticky 参数使组件填满整个单元格
        # 按钮
        self.button2 = ctk.CTkButton(self.score_frame, text="查询", command=self.show_score,fg_color=self.button_color,
                                     font=self.font,hover_color=self.button_hover_color)
        self.button2.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)  # 使用 sticky 参数使组件填满整个单元格
        # 配置按钮框架的列权重，使按钮居中
        self.score_frame.rowconfigure(0, weight=1)
        # self.score_frame.columnconfigure(1, weight=1)
        # 创建只读文本框
        self.score_txt = ctk.CTkTextbox(self.score_frame,height=527,width=435,font=self.font,fg_color='transparent')
        self.score_txt.configure(state=tk.DISABLED)
        self.score_txt.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky=tk.W+tk.E+tk.N+tk.S)  # 使用 sticky 参数使组件填满整个单元格

        #error_frame页面
        self.error_text = ctk.CTkTextbox(self.error_frame, height=530, width=437,font=self.font,fg_color='transparent')
        self.error_text.configure(state=tk.DISABLED)
        self.error_text.grid()

        # ---------------- 设置 ----------------
        self.style=ttk.Style()
        self.style.configure('TLabelframe',background=self.frame_fg_color,borderwidth=10)
        self.style.configure('TLabelframe.Label',background=self.frame_fg_color,font=self.font)
        self.style.configure('TLabel',background=self.frame_fg_color)
        #配置设置
        self.configuration_set_frame=ttk.LabelFrame(self.set_frame, text="配置设置：",relief='ridge')
        self.configuration_set_frame.grid(row=0,column=0,sticky="nsew", padx=5, pady=5)
        #browser
        self.browser_label = ttk.Label(self.configuration_set_frame, text="浏览器:", font=self.font)
        self.browser_label.grid(row=0, column=1, padx=5, pady=10, sticky=tk.W)
        self.browser_options = ["chrome", "edge"]
        self.browser_entry = ctk.CTkComboBox(self.configuration_set_frame,state = 'readonly',
                                             button_color=self.button_color, button_hover_color=self.button_hover_color,
                                             dropdown_fg_color=self.frame_fg_color,
                                             dropdown_hover_color=self.button_color,
                                             values=self.browser_options, font=self.font)
        self.browser_entry.grid(row=0, column=2, padx=5, pady=10, sticky=tk.W)
        # Chrome driver
        self.chrome_driver_label = ttk.Label(self.configuration_set_frame, text="驱动地址:",font=self.font)
        self.chrome_driver_label.grid(row=1, column=1, padx=5, pady=10, sticky=tk.W)
        self.chrome_driver_entry = ctk.CTkEntry(self.configuration_set_frame,width=300)
        self.chrome_driver_entry.grid(row=1, column=2, padx=5, pady=10, sticky=tk.W)
        self.open_file_button = ctk.CTkButton(self.configuration_set_frame, text="选择文件",
                                              fg_color=self.button_color, command=self.select_file,
                                              hover_color=self.button_hover_color)
        self.open_file_button.grid(row=2, column=2, sticky=tk.W)
        #界面设置
        self.frame_set_frame= ttk. LabelFrame(self.set_frame, text="界面设置：")
        self.frame_set_frame.grid(row=1, column=0,  sticky='nsew', padx=5, pady=5)
        #字体设置
        self.frame_font=["Helvetica",'微软雅黑','宋体','楷体','隶书','黑体','仿宋','幼圆','方正舒体','方正姚体','华文彩云','华文琥珀','华文隶书',
                         '华文行楷','华文仿宋','方正新宋体','方正小标宋','楷体_GB2312','仿宋_GB2312','华文中宋','华文新魏','方正仿宋']
        self.font_label = ttk.Label(self.frame_set_frame, text="字体设置：",font=self.font)
        self.font_label.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        self.font_entry = ctk.CTkComboBox(self.frame_set_frame, values= self.frame_font,font=self.font,
                                          button_color=self.button_color, button_hover_color=self.button_hover_color,
                                          dropdown_fg_color=self.frame_fg_color,state = 'readonly',
                                          dropdown_hover_color=self.button_color,
                                          )
        self.font_entry.grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        # 大小设置
        self.size=['9','10','11','12','13','14','15','16']
        self.size_label = ttk.Label(self.frame_set_frame, text="大小设置：",font=self.font)
        self.size_label.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        self.size_entry = ctk.CTkComboBox(self.frame_set_frame, values=self.size, font=self.font,state = 'readonly',
                                          button_color=self.button_color, button_hover_color=self.button_hover_color,
                                            dropdown_fg_color = self.frame_fg_color,
                                            dropdown_hover_color = self.button_color)
        self.size_entry.grid(row=2, column=2, padx=5, pady=5, sticky=tk.W)
        # 窗口置顶勾选框
        self.topmost_label=ttk.Label(self.frame_set_frame, text="窗口置顶：", font=self.font)
        self.topmost_label.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)

        self.topmost_check = ctk.CTkSwitch(self.frame_set_frame, text="",bg_color=self.frame_fg_color,
                                            command=self.toggle_topmost,font=self.font)
        self.topmost_check.grid(row=3,column=2,sticky=tk.W)
        self.topmost_check.select()
        #信息设置
        self.message_set_frame = ttk .LabelFrame(self.set_frame, text="信息设置：")
        self.message_set_frame.grid(row=2,  column=0,  sticky='nsew', padx=5, pady=5)
        # 账户：输入框
        self.phone_number_label = ttk.Label(self.message_set_frame, text="账号:", font=self.font)
        self.phone_number_label.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        self.phone_number_entry = ctk.CTkEntry(self.message_set_frame, font=self.font,)
        self.phone_number_entry.grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        # 密码:输入框
        self.password_label = ttk.Label(self.message_set_frame, text="密码:",font=self.font)
        self.password_label.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        self.password_entry = ctk.CTkEntry(self.message_set_frame, font=self.font,show='*')
        self.password_entry.grid(row=2, column=2, padx=5, pady=5, sticky=tk.W)
        # 输入框：课程
        self.cour_label = ttk.Label(self.message_set_frame, text="课程名称:", font=self.font)
        self.cour_label.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        self.cour_entry = ctk.CTkComboBox(self.message_set_frame, font=self.font,values=[],
                                          button_color=self.button_color, button_hover_color=self.button_hover_color,
                                          dropdown_fg_color=self.frame_fg_color,
                                          dropdown_hover_color=self.button_color,
                                          )
        self.cour_entry['state'] = 'normal'
        self.cour_entry.grid(row=3, column=2, padx=5, pady=5, sticky=tk.W)
        # 刷题：输入框
        self.question_label = ttk.Label(self.message_set_frame, text="刷题设置:", font=self.font)
        self.question_label.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)
        self.question_options = ["大学生搜题酱", "DeepSeek AI","不刷题"]
        self.question_entry = ctk.CTkComboBox(self.message_set_frame, values=self.question_options, font=self.font,
                                              button_color=self.button_color,state = 'readonly',
                                              button_hover_color=self.button_hover_color,
                                              dropdown_fg_color=self.frame_fg_color,
                                              dropdown_hover_color=self.button_color,
                                              )
        # self.question_entry.configure(state = 'readonly')
        self.question_entry.grid(row=4, column=2, padx=5, pady=5, sticky=tk.W)
        #倍速设置：复选框
        self.speed = ['1', '2', '3', '4', '5', '6','8','16']
        self.speed_label = ttk.Label(self.message_set_frame, text="倍速设置：", font=self.font)
        self.speed_label.grid(row=5, column=1, padx=5, pady=5, sticky=tk.W)
        self.speed_entry = ctk.CTkComboBox(self.message_set_frame, values=self.speed, font=self.font,command=self.hint,
                                           button_color=self.button_color, button_hover_color=self.button_hover_color,
                                           dropdown_fg_color=self.frame_fg_color,
                                           dropdown_hover_color=self.button_color,
                                           )
        self.speed_entry.grid(row=5, column=2, padx=5, pady=5, sticky=tk.W)
        self.speed_entry.configure(state = 'readonly')

        self.combobox_lst=[ self.change_theme,self.speed_entry,self.question_entry,self.cour_entry,self.size_entry,
                            self.font_entry, self.browser_entry,self.course_score_entry,self.course_vido_entry]
        # 创建保存按钮
        self.save_button = ctk.CTkButton(self.set_frame, text="保存", command=self.save,
                                         font=self.font,fg_color=self.button_color,
                                         hover_color=self.button_hover_color)
        self.save_button.grid(row=3, column=0, padx=10, pady=10)
        #设置网格权重
        self.set_frame.rowconfigure(3,weight=1)
        self.frame_set_frame.rowconfigure(3,weight=1)
        self.button_name_list1=[self.start_button,self.close_button,self.update_button,self.save_button,
                                self.open_file_button,self.button1,self.button2]

        #----------------帮助页面----------------
        with open(r'task\tool\Help.txt', 'r', encoding='utf-8') as f:
            self.text = f.read()
        self.help_txt = ctk.CTkTextbox(self.help_frame,height=627,width=430,font=self.font,fg_color='transparent')
        self.help_txt.grid()
        self.help_txt.insert(tk.END, self.text)
        self.help_txt.configure(state=tk.DISABLED)

        #----------------赞助页面----------------
        self.label1 = ctk.CTkLabel(self.money_frame, text="如果对您有帮助，欢迎给我打赏,各位的支持就是我更新的最大动力\n(PS:会优先解决打赏的人出现的问题哦！)", font=self.font,fg_color='transparent')
        self.label1.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky=tk.W)
        # 加载图片
        self.image = Image.open(r"task/img/money.png")
        self.photo =ctk.CTkImage(self.image,size=(330,350))

        # 创建标签并显示图片
        self.label = ctk.CTkLabel(self.money_frame,text='' ,image=self.photo,fg_color='transparent')
        self.label.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky=tk.W+tk.E)

        # 更新时间显示
        self.update_time()
        self.load_data()
        self.show_main()

    def select_frame_by_name(self, name):
        # set button color for selected button
            for i in range(len(self.button_name_list)-2):
                txt = self.button_text_list[i]
                self.button_name_list[i].configure(fg_color=self.color_value_dict.get(self.change_theme.get())[0] if name == txt else "transparent")

    def check_update(self):
        self.text_box.configure(state=tk.NORMAL)
        # 清空文本框内容
        self.text_box.delete('1.0', tk.END)
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
                assets = release_info.get('assets', [])
                if assets:
                    self.text_box.insert(tk.END, '连接成功\n')
                    # 获取第一个文件
                    first_asset = assets[0]
                    download_url = first_asset['browser_download_url']
                    file_name = first_asset['name']

                    # 读取当前版本信息
                    with open('task/tool/version_info', 'r') as f:
                        version = f.read()

                    if version == file_name:
                        self.text_box.insert(tk.END, '当前版本为最新版本，无需更新\n')
                        return False
                    else:
                        self.result = tk.messagebox.askokcancel(
                            '确认更新', '已检测到新版本，是否更新？')
                        if self.result:
                            self.text_box.insert(tk.END, '开始更新(大约1分钟)...\n')

                            def update(thread_event):
                                start_time = time.time()
                                self.text_box.insert(tk.END, '下载中...\n')

                                # 父级的父级目录路径
                                grandparent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
                                download_path = os.path.join(grandparent_dir, file_name)  # 父级的父级目录中的下载路径
                                try:
                                    self.progress_bar.set(0)
                                    self.progress_label.grid(row=2, column=0, columnspan=3, padx=10, pady=10,
                                                             sticky=tk.W)
                                    self.progress_bar.grid(row=2, column=1, columnspan=3, pady=10, sticky=tk.W)

                                    # 下载文件到父级的父级目录
                                    with requests.get(download_url, stream=True) as r:
                                        r.raise_for_status()
                                        with open(download_path, 'wb') as f:
                                            for chunk in r.iter_content(chunk_size=8192):
                                                f.write(chunk)
                                    self.text_box.insert(tk.END, f'下载成功, 文件保存到 {download_path}\n')
                                    try:
                                        # 解压文件到父级的父级目录，保留文件夹结构
                                        self.text_box.insert(tk.END, '开始解压...\n')
                                        extracted_folder_name = os.path.splitext(file_name)[0]  # 假设文件名不包含复杂扩展
                                        extraction_path = os.path.join(grandparent_dir, extracted_folder_name)
                                        os.makedirs(extraction_path, exist_ok=True)  # 创建目标文件夹
                                        shutil.unpack_archive(download_path, extraction_path)
                                        os.remove(download_path)  # 删除下载的压缩文件
                                        self.text_box.insert(tk.END, f"解压成功，文件夹路径：{extraction_path}\n")

                                        # 更新版本信息
                                        with open('task/tool/version_info', 'w') as f:
                                            f.write(file_name)
                                        end_time = time.time()
                                        self.text_box.insert(tk.END,
                                                             f"更新成功，用时 {end_time - start_time:.2f} 秒\n请关闭该脚本并前往解压后的地址使用新版本\n")
                                        self.progress_bar.set(1)
                                        thread_event.set()
                                        self.progress_label.configure(text="当前进度：100.0%")
                                        self.progress_label.update()
                                        tk.messagebox.showinfo("提示", "请关闭该脚本并前往解压后的地址使用新版本！")
                                    except Exception as e:
                                        self.text_box.insert(tk.END, f"解压失败: {str(e)}\n请自行前往{download_path}解压")
                                except Exception as e:
                                    self.text_box.insert(tk.END,
                                                         f"更新失败: {str(e)}\n请检查或更换网络\n或自行前往\nhttps://github.com/Mortal004/Xuexitong_shuake/releases/tag"
                                                         "\n或夸克网盘：https://pan.quark.cn/s/eba634db1544\n或百度网盘: https://pan.baidu.com/s/1wbkc_07BqqQuwxri2WJtew?pwd=1234 下载")
                                # 隐藏进度条
                                    thread_event.set()
                                self.progress_bar.grid_forget()
                                self.progress_label.grid_forget()
                            # 使用线程运行更新操作
                            def fake_progress(thread_event):
                                progress = 0
                                while progress <= 0.99 and not thread_event.is_set():
                                    self.progress_bar.set(progress)
                                    self.progress_bar.update()
                                    # 更新标签显示的进度
                                    self.progress_label.configure(
                                        text=f"当前进度：{progress * 100:.2f}%")
                                    self.progress_label.update()
                                    if progress <= 0.6:
                                        progress += 0.0015
                                        time.sleep(0.04)
                                    else:
                                        progress += 0.001
                                        time.sleep(0.06)
                                if "{:.2f}".format(progress*100 ) == '99.05' :
                                    self.text_box.insert(tk.END, '当前网速较慢，请耐心等待...\n')
                            event=threading.Event()
                            fake_thread = threading.Thread(target=fake_progress,args=(event,))
                            update_thread = threading.Thread(target=update,args=(event,))
                            fake_thread.start()
                            update_thread.start()
                        else:
                            self.text_box.insert(tk.END, '已取消更新\n')
                            return False
                else:
                    self.text_box.insert(tk.END, "Release中没有找到文件\n")
            else:
                self.text_box.insert(tk.END, "Release中没有找到文件\n")
        except requests.RequestException as e:
            self.text_box.insert(
                tk.END,
                f"检查更新时发生错误: {str(e)}\n请尝试开启或关闭加速器，或者检查或更换网络\n或自行前往\nhttps://github.com/Mortal004/Xuexitong_shuake/releases/tag"
                "\n或夸克网盘：https://pan.quark.cn/s/eba634db1544\n或百度网盘: https://pan.baidu.com/s/1wbkc_07BqqQuwxri2WJtew?pwd=1234 下载")

    def toggle_topmost(self):
        """切换窗口始终置顶属性"""
        if self.topmost_check.get():
            self.is_topmost = False
            self.root.wm_attributes("-topmost", True)
        else:
            self.is_topmost = True
            self.root.wm_attributes("-topmost", False)

    def show_main(self):
        self.select_frame_by_name('主页')
        self.main_frame.grid(row=1, column=1,sticky='nsew')
        self.error_frame.grid_forget()
        self.score_frame.grid_forget()
        self.vido_frame.grid_forget()
        self.set_frame.grid_forget()
        self.help_frame.grid_forget()
        self.money_frame.grid_forget()

    def show_vido(self,*key):
        self.select_frame_by_name('刷课日志')
        self.vido_text.configure(state=tk.NORMAL)
        try:
            with open(fr'task\record\《{self.course_vido_entry.get()}》的刷课记录.txt', 'r', encoding='utf-8') as f:
                content = f.read()
                self.vido_text.delete('1.0', tk.END)
                self.vido_text.insert(tk.END, content)
        except FileNotFoundError:
            self.vido_text.delete('1.0', tk.END)
            self.vido_text.insert(tk.END, f'暂未查询到《{self.course_vido_entry.get()}》的刷课记录')
        self.vido_frame.grid(row=1, column=1,sticky='nsew')
        self.error_frame.grid_forget()
        self.score_frame.grid_forget()
        self.main_frame.grid_forget()
        self.set_frame.grid_forget()
        self.help_frame.grid_forget()
        self.money_frame.grid_forget()
        self.vido_text.configure(state=tk.DISABLED)

    def show_score(self,*key):
        self.select_frame_by_name('测试成绩')
        self.score_txt.configure(state=tk.NORMAL)
        try:
            with open(fr'task\record\《{self.course_score_entry.get()}》的成绩记录.txt', 'r', encoding='utf-8') as f:
                content = f.read()
                self.score_txt.delete('1.0', tk.END)
                self.score_txt.insert(tk.END, content)
        except FileNotFoundError:
            self.score_txt.delete('1.0', tk.END)
            self.score_txt.insert(tk.END, f'暂未查询到《{self.course_score_entry.get()}》的成绩记录')
        self.score_frame.grid(row=1, column=1,sticky='nsew')
        self.error_frame.grid_forget()
        self.main_frame.grid_forget()
        self.vido_frame.grid_forget()
        self.set_frame.grid_forget()
        self.help_frame.grid_forget()
        self.money_frame.grid_forget()
        self.score_txt.configure(state=tk.DISABLED)

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
        self.error_frame.grid(row=1, column=1,sticky='nsew')
        self.score_frame.grid_forget()
        self.main_frame.grid_forget()
        self.vido_frame.grid_forget()
        self.set_frame.grid_forget()
        self.help_frame.grid_forget()
        self.money_frame.grid_forget()
        self.error_text.configure(state=tk.DISABLED)

    def show_set(self):
        self.select_frame_by_name('设置')
        self.set_frame.grid(row=1, column=1,sticky='nsew')
        self.error_frame.grid_forget()
        self.score_frame.grid_forget()
        self.main_frame.grid_forget()
        self.vido_frame.grid_forget()
        self.help_frame.grid_forget()
        self.money_frame.grid_forget()

    def show_money(self):
        self.select_frame_by_name('赞助作者')
        self.money_frame.grid(row=1, column=1)
        self.error_frame.grid_forget()
        self.score_frame.grid_forget()
        self.main_frame.grid_forget()
        self.vido_frame.grid_forget()
        self.set_frame.grid_forget()
        self.help_frame.grid_forget()

    def select_file(self):
        file_path = filedialog.askopenfilename(title="选择文件", filetypes=[("", "*.exe")])
        if file_path:
            self.chrome_driver_entry.delete(0, tk.END)
            self.chrome_driver_entry.insert(tk.END,file_path)

    def show_help(self):
        self.select_frame_by_name('帮助')
        self.help_frame.grid(row=1, column=1,sticky='nsew')
        self.set_frame.grid_forget()
        self.error_frame.grid_forget()
        self.score_frame.grid_forget()
        self.main_frame.grid_forget()
        self.vido_frame.grid_forget()
        self.money_frame.grid_forget()

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

    def close(self):
        self.reopen_frame()
        if self.process is not None:
            try:
                if os.name == 'nt':  # Windows 平台
                    subprocess.run(['taskkill', '/F', '/T', '/PID', str(self.process.pid)])
                else:  # Unix 平台
                    os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                self.text_box.insert(tk.END, "程序已成功关闭\n")
            except Exception as e:
                self.text_box.insert(tk.END, f"关闭失败: {e}\n")
            finally:
                process = None

    # 每秒更新 GUI 中的时间显示
    def update_time(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.configure(text=f"当前时间: {current_time}")
        self.root.after(1000, self.update_time)  # 每秒更新一次

    def change_font(self):
        self.font = (self.font_entry.get(), self.size_entry.get())
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
        content =self.cour_entry.get()
        if content:
            data = []
            try:
                with open(r'task\tool\course_name.json', 'r') as f:
                    data = json.load(f)
            except FileNotFoundError:
                pass
            if content not in data:
                data.append(content)
                with open(r'task\tool\course_name.json', 'w' , encoding='utf-8')as f:
                    json.dump(data, f)

    def save(self):
        try:
            with open(r'task\tool\account_info.json', 'r', encoding='utf-8') as f:
                self.account_info = json.load(f)
        except FileNotFoundError:
            self.account_info = {}
        if self.browser_entry.get()=='':
            tk.messagebox.showerror('警告', message='请选择浏览器')
            return False
        else:
            self.account_info['browser']=self.browser_entry.get()
        if self.chrome_driver_entry.get()=='':
            tk.messagebox.showerror('警告', message='请填写驱动的地址')
            return False
        else:
            self.account_info['driver_path']=self.chrome_driver_entry.get()
        if self.browser_entry.get() not in self.chrome_driver_entry.get():
            tk.messagebox.showerror('警告', message='请检查你的浏览器是否与驱动对应')
            return False

        if self.phone_number_entry.get()=='':
            tk.messagebox.showerror('警告', message='请填写手机号')
            return False
        else:
            self.account_info['phone_number'] = self.phone_number_entry.get()
        if  self.password_entry.get()=='':
            tk.messagebox.showerror('警告', message='请填写密码')
            return False
        else:
            self.account_info['password'] = self.password_entry.get()
        if self.cour_entry.get()=='':
            tk.messagebox.showerror('警告', message='请填写课程名称')
            return False
        else:
            self.account_info['cour'] = self.cour_entry.get()
        if self.question_entry.get() =='' :
            tk.messagebox.showerror('警告', message='请选择选择刷题设置')
            return False
        else:
            self.account_info['choice'] = self.question_entry.get()
        if self.speed_entry.get()=='':
            tk.messagebox.showerror('警告', message='请填写倍数')
            return False
        else:
            self.account_info['speed']=self.speed_entry.get()
        self.account_info['font_type'] = self.font_entry.get()
        self.account_info['font_size'] = self.size_entry.get()
        if self.question_entry.get() != '不刷题':
            self.result = tk.messagebox.askokcancel('确认保存', '你确定要保存吗？\n(注意：搜题暂时只能搜索选择题和判断题)')
        else:
            self.result = tk.messagebox.askokcancel('确认保存', '你确定要保存吗？')
        if self.result:
            tk.messagebox.showinfo('', '保存成功')
            with open(r'task\tool\account_info.json', 'w', encoding='utf-8') as f:
                json.dump(self.account_info, f)
            self.save_course()
            self.change_font()
            self.root.update()

    def load_data(self):
        try:
            with open(r'task\tool\course_name.json', 'r') as f:
                data = json.load(f)
                if data:
                    self.course_score_entry.configure(values= tuple(data))
                    self.course_vido_entry.configure(values= tuple(data))
                    self.cour_entry.configure(values= tuple(data))
            with open(r'task\tool\account_info.json', 'r', encoding='utf-8') as fil:
                self.account_info = json.load(fil)
                self.course_score_entry.set( self.account_info['cour'])
                self.course_vido_entry.set( self.account_info['cour'])
                self.browser_entry.set( self.account_info['browser'])
                self.chrome_driver_entry.insert(0, self.account_info['driver_path'])
                self.speed_entry.set( self.account_info['speed'])
                self.phone_number_entry.insert( 0,self.account_info['phone_number'])
                self.password_entry.insert(0, self.account_info['password'])
                self.cour_entry.set( self.account_info['cour'])
                self.question_entry.set( self.account_info['choice'])

                try:
                    self.font_entry.set(self.account_info['font_type'])
                    self.size_entry.set(self.account_info['font_size'])
                    self.change_font()
                except:
                    pass
        except FileNotFoundError:
            pass

    def fold_frame(self):
        self.navigation_frame.grid_forget()
        self.open_frame.grid(row=0, column=0,rowspan=2, sticky="ns")

    def reopen_frame(self):
        self.open_frame.grid_forget()
        self.navigation_frame.grid(row=0, column=0, rowspan=2,sticky="nsew")

    def change_appearance_mode_event(self, theme):
        self.record_color_lst.append(theme)
        for frame in self.frame_name_list:
            frame.configure(fg_color=self.color_value_dict.get(theme)[1])
        self.style.configure('TLabelframe', background=self.color_value_dict.get(theme)[1])
        self.style.configure('TLabelframe.Label', background=self.color_value_dict.get(theme)[1])
        self.style.configure('TLabel',background=self.color_value_dict.get(theme)[1])
        self.topmost_check.configure(bg_color=self.color_value_dict.get(theme)[1],progress_color=self.color_value_dict.get(theme)[0])
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

