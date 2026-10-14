"""设置页面 — 配置、账号、功能、高级设置的全部 UI 和交互逻辑"""
import json
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image
from gui.tooltip import ToolTip

class SettingsPanel:
    def __init__(self, parent, config_manager, change_font,change_text_box,
                 get_font, get_colors, get_theme, show_money, root,_timer):
        self.timer_end_time = '03:00:00'
        self.timer_start_time = '04:00:00'
        self.parent = parent
        self.config = config_manager
        self.change_font = change_font
        self.change_text_box=change_text_box
        self._get_font = get_font
        self._get_colors = get_colors
        self._get_theme = get_theme
        self._show_money = show_money
        self.root = root
        self._timer=_timer
        self.is_topmost = True
        self.root.wm_attributes("-topmost", self.is_topmost)
        self.radio_var = tk.IntVar(value=1)
        self.dynamic_rows = []
        self.next_row = 4
        self.all_courses = []
        self.data = []
        self.pady = 7
        self._build_ui()

    @property
    def _font(self): return self._get_font()

    @property
    def _colors(self): return self._get_colors()

    @property
    def _theme_colors(self): return self._get_theme()

    def _build_ui(self):
        c = self._colors
        f = self._font
        bg = self._theme_colors[1]

        cfg = ctk.CTkFrame(self.parent, corner_radius=12, border_width=1,
                           fg_color='transparent', border_color="#CBD5E1")
        cfg.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        ctk.CTkLabel(cfg, text="⚙ 配置设置", font=("Microsoft YaHei", 13, "bold")).grid(
            row=0, column=0, columnspan=3, sticky="w", padx=12, pady=(8, 4))

        ctk.CTkLabel(cfg, text="浏览器:", font=f).grid(row=1, column=0, padx=6, pady=4, sticky="w")
        self.browser_entry = ctk.CTkComboBox(
            cfg, values=['不指定浏览器', 'edge', 'chrome'], state='readonly',
            font=f, corner_radius=6, dropdown_fg_color=bg,
            dropdown_hover_color=c[0], button_color=c[0],
            button_hover_color=c[2], command=self._auto_fill_browser_driver)
        self.browser_entry.grid(row=1, column=1, padx=6, pady=4, sticky="w")

        ctk.CTkLabel(cfg, text="驱动地址:", font=f).grid(row=2, column=0, padx=6, pady=4, sticky="w")
        self.browser_driver_entry = ctk.CTkEntry(cfg, corner_radius=6, width=140)
        self.browser_driver_entry.grid(row=2, column=1, padx=6, pady=4, sticky="w")
        self.open_file_button = ctk.CTkButton(
            cfg, text="📁  选择文件", width=140, fg_color=c[0],
            hover_color=c[2], corner_radius=6, command=self._select_file)
        self.open_file_button.grid(row=3, column=1, padx=6, pady=4, sticky="w")

        ui = ctk.CTkFrame(self.parent, corner_radius=12, border_width=1,
                          fg_color='transparent', border_color="#CBD5E1")
        ui.grid(row=1, column=0, sticky="nsew", padx=6, pady=6)
        ctk.CTkLabel(ui, text="🖥 界面设置", font=("Microsoft YaHei", 13, "bold")).grid(
            row=0, column=0, columnspan=3, sticky="w", padx=6, pady=(8, 4))

        ctk.CTkLabel(ui, text="字体设置:", font=f).grid(row=1, column=0, padx=6, pady=4, sticky="w")
        self.font_entry = ctk.CTkComboBox(
            ui, values=["Helvetica", "Microsoft YaHei", '微软雅黑', '宋体', '楷体', '黑体'],
            dropdown_fg_color=bg, dropdown_hover_color=c[0], state='readonly',
            font=f, corner_radius=6, button_color=c[0], button_hover_color=c[2])
        self.font_entry.grid(row=1, column=1, padx=6, pady=4, sticky="w")

        ctk.CTkLabel(ui, text="大小设置:", font=f).grid(row=2, column=0, padx=6, pady=4, sticky="w")
        self.size_entry = ctk.CTkComboBox(
            ui, values=['9','10','11','12','13','14','15','16'],
            dropdown_fg_color=bg, dropdown_hover_color=c[0], state='readonly',
            font=f, corner_radius=6, button_color=c[0], button_hover_color=c[2])
        self.size_entry.grid(row=2, column=1, padx=6, pady=4, sticky="w")

        ctk.CTkLabel(ui, text="窗口置顶:", font=f).grid(row=3, column=0, padx=6, pady=4, sticky="w")
        self.topmost_check = ctk.CTkSwitch(ui, text="", command=self._toggle_topmost)
        self.topmost_check.grid(row=3, column=1, padx=6, pady=4, sticky="w")
        self.topmost_check.select()

        self._build_account_section(bg, c, f)
        self._build_function_section(bg, c, f)
        self._build_detail_section(bg, c, f)

        self.save_button = ctk.CTkButton(
            self.parent, text="💾 保存设置", command=self.save,
            font=("Microsoft YaHei", 13, "bold"), height=40,
            corner_radius=20, fg_color=c[0], hover_color=c[2])
        self.save_button.grid(row=3, column=0, columnspan=2, pady=20, padx=12)
        self.parent.rowconfigure(3, weight=1)
        ui.rowconfigure(3, weight=1)

    def _toggle_topmost(self):
        if self.topmost_check.get():
            self.is_topmost = False
            self.root.wm_attributes("-topmost", True)
        else:
            self.is_topmost = True
            self.root.wm_attributes("-topmost", False)

    def _build_account_section(self, bg, c, f):
        msg = ctk.CTkFrame(self.parent, corner_radius=12, border_width=1,
                           fg_color='transparent', border_color="#CBD5E1")
        msg.grid(row=2, column=0, sticky="nsew", padx=6, pady=6)
        ctk.CTkLabel(msg, text="👤 账号信息", font=("Microsoft YaHei", 13, "bold")).grid(
            row=0, column=0, columnspan=3, sticky="w", padx=6, pady=(8, 4))

        ctk.CTkLabel(msg, text="账号:", font=f).grid(row=1, column=0, padx=6, pady=4, sticky="w")
        self.phone_number_entry = ctk.CTkEntry(msg, corner_radius=6, width=140)
        self.phone_number_entry.grid(row=1, column=1, padx=6, pady=4, sticky="w")

        ctk.CTkLabel(msg, text="密码:", font=f).grid(row=2, column=0, padx=6, pady=4, sticky="w")
        self.password_entry = ctk.CTkEntry(msg, show='*', corner_radius=6, width=140)
        self.password_entry.grid(row=2, column=1, padx=(6, 0), pady=4, sticky="w")
        show_img = ctk.CTkImage(light_image=Image.open(r"task\img\show.png"), size=(16, 12))
        self.show_pwd_btn = ctk.CTkButton(msg, text="", fg_color='transparent',
                                          image=show_img, command=self._show_password,
                                          font=f, width=5, height=10)
        self.show_pwd_btn.grid(row=2, column=2, padx=0, pady=4, sticky=tk.W)

        ctk.CTkLabel(msg, text="课程名称:", font=f).grid(row=3, column=0, padx=6, pady=4, sticky="w")
        self.cour_entry = ctk.CTkComboBox(
            msg, values=[], state='normal', dropdown_fg_color=bg,
            dropdown_hover_color=c[0], font=f, corner_radius=6, button_color=c[0])
        self.cour_entry.grid(row=3, column=1, padx=6, pady=4, sticky="w")
        add_img = ctk.CTkImage(light_image=Image.open(r"task\img\add.png"), size=(18, 19))
        self.add_course_btn = ctk.CTkButton(
            msg, text="", fg_color='transparent', image=add_img,
            command=lambda: self.add_course(''), width=5, height=5)
        self.add_course_btn.grid(row=3, column=2, padx=1, pady=4, sticky=tk.W)
        ToolTip(self.add_course_btn, "添加课程")
        self.message_set_frame = msg

    def _build_function_section(self, bg, c, f):
        func = ctk.CTkFrame(self.parent, corner_radius=12, border_width=1,
                            fg_color='transparent', border_color="#CBD5E1")
        func.grid(row=0, column=1, sticky="nsew", padx=6, pady=6)
        ctk.CTkLabel(func, text="🚀 功能设置", font=("Microsoft YaHei", 13, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=6, pady=(8, 4))
        self.radio_button_1 = ctk.CTkRadioButton(
            func, text="自动刷课答题", variable=self.radio_var, value=1,
            command=self.function_choice, font=f)
        self.radio_button_2 = ctk.CTkRadioButton(
            func, text="自动完成作业", variable=self.radio_var, value=2,
            command=self.function_choice, font=f)
        self.radio_button_3 = ctk.CTkRadioButton(
            func, text="自动完成考试", variable=self.radio_var, value=3,
            command=self.function_choice, font=f)
        self.radio_button_1.grid(row=1, column=1, columnspan=3, padx=12, pady=6, sticky="w")
        self.radio_button_2.grid(row=2, column=1, columnspan=3, padx=12, pady=6, sticky="w")
        self.radio_button_3.grid(row=3, column=1, columnspan=3, padx=12, pady=6, sticky="w")
        self.function_set_frame = func

    def _build_detail_section(self, bg, c, f):
        det = ctk.CTkFrame(self.parent, corner_radius=12, border_width=1,
                           fg_color='transparent', border_color="#CBD5E1")
        det.grid(row=1, column=1, rowspan=2, sticky="nsew", padx=6, pady=6)
        ctk.CTkLabel(det, text="🔧 高级设置", font=("Microsoft YaHei", 13, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=6, pady=(8, 4))

        self.question_label = ctk.CTkLabel(det, text="章节测验:", font=f)
        self.question_entry = ctk.CTkComboBox(
            det, values=["DeepSeek AI", '随机答题', "不刷题"],
            dropdown_fg_color=bg, dropdown_hover_color=c[0], font=f,
            corner_radius=6, state='readonly', button_color=c[0],
            command=self.shua_ti_choice)

        self.after_finish_question = ctk.CTkLabel(det, text="答完题后:", font=f)
        self.after_finish_question_entry = ctk.CTkComboBox(
            det, values=["仅自动保存", '强制自动提交', '搜到60%的题自动提交',
                         '搜到70%的题自动提交', '搜到80%的题自动提交',
                         '搜到90%的题自动提交', '搜到100%的题自动提交'],
            dropdown_fg_color=bg, dropdown_hover_color=c[0], font=f,
            corner_radius=6, state='readonly', button_color=c[0])

        self.vido_question_label = ctk.CTkLabel(det, text="视频题目:", font=f)
        self.vido_question_entry = ctk.CTkComboBox(
            det, values=["DeepSeek AI", '随机答题'],
            dropdown_fg_color=bg, dropdown_hover_color=c[0], font=f,
            corner_radius=6, state='readonly', button_color=c[0],
            command=lambda _: self.shua_ti_choice('视频题目'))

        self.discussion_label = ctk.CTkLabel(det, text="讨论:", font=f)
        self.discussion_entry = ctk.CTkComboBox(
            det, values=["DeepSeek AI", '跳过讨论'],
            dropdown_fg_color=bg, dropdown_hover_color=c[0], font=f,
            corner_radius=6, state='readonly', button_color=c[0],
            command=lambda _: self.shua_ti_choice('讨论'))

        self.speed_label = ctk.CTkLabel(det, text="倍速设置:", font=f)
        self.speed_entry = ctk.CTkComboBox(
            det, values=['1','2','3','4','5','6','8','10','16'],
            dropdown_fg_color=bg, dropdown_hover_color=c[0], font=f,
            corner_radius=6, state='readonly', command=self._hint, button_color=c[0])

        self.API_label = ctk.CTkLabel(det, text="API Key:", font=f)
        self.API_entry = ctk.CTkEntry(det, show='*', corner_radius=6)
        ToolTip(self.API_entry, "可通过赞助作者获取或者前往deepseek官网购买")
        show_img = ctk.CTkImage(light_image=Image.open(r"task\img\show.png"), size=(16, 12))
        self.show_api_btn = ctk.CTkButton(det, text="", fg_color='transparent',
                                          image=show_img, command=self._show_api,
                                          font=f, width=5, height=10)

        self.pass_face_label = ctk.CTkLabel(det, text="跳过人脸:", font=f)
        self.pass_face_check = ctk.CTkSwitch(det, text="",)
        ToolTip(self.pass_face_check, "只有当你的课程需要人脸认证时才开启")

        self.multi_device_label = ctk.CTkLabel(det, text="多端学习:", font=f)
        self.multi_device_check = ctk.CTkSwitch(det, text="",width=20,command=self._warn)
        ToolTip(self.multi_device_check, "解除多端学习监控，可同时刷多门课程")

        self.pass_vido_label = ctk.CTkLabel(det, text='秒过视频:', font=f)
        self.pass_vido_check = ctk.CTkSwitch(det, text="", command=self._change_speed,)
        ToolTip(self.pass_vido_check, "只有在视频可以拖动进度条的情况下\n才会有效")

        self.lock_screen_label = ctk.CTkLabel(det, text="防锁屏:", font=f)
        self.lock_screen_check = ctk.CTkSwitch(det, text="",width=20)

        self.timer_label=ctk.CTkLabel(det,text='定时刷课:',font=f)
        self.timer_check=ctk.CTkSwitch(det, text="",command=self.open_timer_window,)

        self.homework_label = ctk.CTkLabel(det, text="选择作业:", font=f)
        self.homework_entry = ctk.CTkComboBox(
            det, values=['手动选择', '自动选择'],
            dropdown_fg_color=bg, dropdown_hover_color=c[0], state='readonly',
            font=f, corner_radius=6, command=self._prompt, button_color=c[0])
        self.detail_set_frame = det

    def open_timer_window(self):
        if self.timer_check.get():
            self._timer.open(self.timer_start_time, self.timer_end_time)
        else:
            self._timer.cancel()

    def _warn(self):
        if self.multi_device_check.get():
            tk.messagebox.showwarning('警告','请谨慎开启，开启后有可能会清空课程进度，甚至直接挂科，'
                                         '如果不是实在刷不完，还请老老实实一科一科的刷,一切后果自负')

    def _change_speed(self):
        if self.pass_vido_check.get():
            self.speed_entry.set('1')
            self.speed_entry.configure(state='disabled')
            messagebox.showinfo('提示', '只有在视频可以拖动进度条的情况下才会有效')
        else:
            self.speed_entry.configure(state='normal')

    def add_course(self, cour_name):
        row = self.next_row
        self.next_row += 1
        if row >= 6:
            messagebox.showwarning('警告', '最多只能添加3门课程')
            self.next_row -= 1
            return
        c, f, bg = self._colors, self._font, self._theme_colors[1]
        entry = ctk.CTkComboBox(
            self.message_set_frame, values=self.data, state='normal',
            dropdown_fg_color=bg, dropdown_hover_color=c[0],
            font=f, corner_radius=6, button_color=c[0])
        entry.set(cour_name)
        entry.grid(row=row, column=1, padx=6, pady=4, sticky="w")
        del_btn = ctk.CTkButton(
            self.message_set_frame, text="✖", width=20,
            fg_color="#F87171", hover_color="#EF4444",
            command=lambda: self._delete_course_row(entry, del_btn, row))
        del_btn.grid(row=row, column=2, padx=2, pady=4, sticky=tk.W)
        tip = ToolTip(del_btn, "删除该课程")
        self.dynamic_rows.append((entry, del_btn, row, tip))
        if row == 5 and len(self.dynamic_rows) >= 2:
            prev_entry, prev_del_btn, prev_row, prev_tip = self.dynamic_rows[-2]
            prev_del_btn.configure(state='disabled')
            prev_tip.set_text("请先删除最后一个课程")

    def _delete_course_row(self, entry, del_btn, row):
        entry.destroy()
        del_btn.destroy()
        for i, (e, d, r, tip) in enumerate(self.dynamic_rows):
            if e == entry:
                self.dynamic_rows.pop(i)
                break
        self.next_row -= 1
        if self.next_row == 5 and len(self.dynamic_rows) >= 1:
            last_entry, last_del_btn, last_row, last_tip = self.dynamic_rows[-1]
            last_del_btn.configure(state='normal')
            last_tip.set_text("删除该课程")

    def function_choice(self):
        if self.radio_var.get() == 1:
            self._show_brush_mode()
        elif self.radio_var.get() == 2:
            self._show_homework_mode()
        else:
            messagebox.showinfo('提示', '该功能还在开发中...,敬请期待')
            self.radio_var.set(1)
            self.function_choice()

    def _show_brush_mode(self):
        self.question_label.configure(text='章节测验:')
        self.question_label.grid(row=4, column=1, padx=5, pady=self.pady, sticky=tk.W)
        self.question_entry.grid(row=4, column=2, padx=5, pady=self.pady, sticky=tk.W)
        if self.question_entry.get() == 'DeepSeek AI':
            self.after_finish_question.grid(row=5, column=1, padx=5, pady=self.pady, sticky=tk.W)
            self.after_finish_question_entry.grid(row=5, column=2, padx=5, pady=self.pady, sticky=tk.W)
        self.after_finish_question_entry.configure(values=[
            "仅自动保存", '强制自动提交', '搜到60%的题自动提交',
            '搜到70%的题自动提交', '搜到80%的题自动提交',
            '搜到90%的题自动提交', '搜到100%的题自动提交'])
        self.vido_question_label.grid(row=6, column=1, padx=5, pady=self.pady, sticky=tk.W)
        self.vido_question_entry.grid(row=6, column=2, padx=5, pady=self.pady, sticky=tk.W)
        self.discussion_label.grid(row=7, column=1, padx=5, pady=self.pady, sticky=tk.W)
        self.discussion_entry.grid(row=7, column=2, padx=5, pady=self.pady, sticky=tk.W)
        self.question_entry.configure(values=['DeepSeek AI', '随机答题', '不刷题'])
        if any(e.get() == 'DeepSeek AI' for e in
               [self.question_entry, self.vido_question_entry, self.discussion_entry]):
            self.API_label.grid(row=8, column=1, padx=5, pady=self.pady, sticky=tk.W)
            self.API_entry.grid(row=8, column=2, padx=5, pady=self.pady, sticky=tk.W)
            self.show_api_btn.grid(row=8, column=3, pady=self.pady, sticky=tk.W)
        self.speed_label.grid(row=9, column=1, padx=5, pady=self.pady, sticky=tk.W)
        self.speed_entry.grid(row=9, column=2, padx=5, pady=self.pady, sticky=tk.W)
        self.pass_face_label.grid(row=10, column=1, padx=5, pady=5, sticky=tk.W)
        self.pass_face_check.grid(row=10, column=2, padx=0, pady=5, sticky=tk.W)
        self.multi_device_label.grid(row=10, column=2, padx=5, pady=5, sticky=tk.E)
        self.multi_device_check.grid(row=10, column=3, padx=0, pady=5, sticky=tk.W)
        self.pass_vido_label.grid(row=11, column=1, padx=5, pady=5, sticky=tk.W)
        self.pass_vido_check.grid(row=11, column=2, padx=0, pady=5, sticky=tk.W)
        self.lock_screen_label.grid(row=11, column=2, padx=5, pady=5, sticky=tk.E)
        self.lock_screen_check.grid(row=11, column=3, padx=0, pady=5, sticky=tk.W)
        self.timer_label.grid(row=12, column=1, padx=5, pady=self.pady, sticky=tk.W)
        self.timer_check.grid(row=12, column=2, padx=0, pady=5, sticky=tk.W)
        self.homework_label.grid_forget()
        self.homework_entry.grid_forget()

    def _show_homework_mode(self):
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
        self.show_api_btn.grid(row=7, column=3, pady=self.pady, sticky=tk.W)
        self.homework_label.grid(row=9, column=1, padx=5, pady=self.pady, sticky=tk.W)
        self.homework_entry.grid(row=9, column=2, padx=5, pady=self.pady, sticky=tk.W)
        for w in [self.speed_label, self.speed_entry, self.lock_screen_label,
                  self.lock_screen_check, self.vido_question_label,
                  self.vido_question_entry, self.discussion_label,
                  self.discussion_entry, self.pass_vido_label, self.pass_vido_check]:
            w.grid_forget()

    def shua_ti_choice(self, event=None):
        if self.question_entry.get() == '随机答题' and event not in ('视频题目', '讨论'):
            messagebox.showinfo('提示', '请谨慎选择，只有在章节测验不计入总成绩的情况下才能使用...')
        if self.question_entry.get() != 'DeepSeek AI':
            self.after_finish_question.grid_forget()
            self.after_finish_question_entry.grid_forget()
        else:
            self.after_finish_question.grid(row=5, column=1, padx=5, pady=self.pady, sticky=tk.W)
            self.after_finish_question_entry.grid(row=5, column=2, padx=5, pady=self.pady, sticky=tk.W)
        need_api = any(e.get() == 'DeepSeek AI' for e in
                       [self.question_entry, self.vido_question_entry, self.discussion_entry])
        if need_api:
            if self.vido_question_entry.get() == 'DeepSeek AI' and event == '视频题目':
                messagebox.showinfo('提示', '用于完成视频中弹出的题目...'
                                            '只有在选错答案会回退视频的情况下才建议使用DeepSeek AI，一般情况请使用随机答题,没有任何影响')
            self.API_label.grid(row=8, column=1, padx=5, pady=5, sticky=tk.W)
            self.API_entry.grid(row=8, column=2, padx=5, pady=5, sticky=tk.W)
            self.show_api_btn.grid(row=8, column=3, pady=5, sticky=tk.W)
        else:
            for w in [self.API_label, self.API_entry, self.show_api_btn]:
                w.grid_forget()

    def _auto_fill_browser_driver(self, choice):
        self.browser_driver_entry.configure(state='normal')
        self.browser_driver_entry.delete(0, tk.END)
        if choice == "edge":
            self.browser_driver_entry.insert(0, r"edgedriver_win64\msedgedriver.exe")
        elif choice == "不指定浏览器":
            self.browser_driver_entry.insert(0, "无需填写")
            self.browser_driver_entry.configure(state='disabled')

    def _select_file(self):
        path = filedialog.askopenfilename(title="选择文件", filetypes=[("", "*.exe")])
        if path:
            self.browser_driver_entry.delete(0, tk.END)
            self.browser_driver_entry.insert(tk.END, path)

    def _show_password(self):
        self.password_entry.configure(
            show='' if self.password_entry.cget('show') == '*' else '*')

    def _show_api(self):
        self.API_entry.configure(
            show='' if self.API_entry.cget('show') == '*' else '*')

    def _hint(self, speed):
        if int(speed) > 2:
            messagebox.showinfo('提示', '倍数过高，已完成的任务点可能会被清空，请谨慎使用')

    def _prompt(self, choice):
        if choice == '自动选择':
            messagebox.showinfo('提示', '默认会从第一个未完成的作业开始刷...')
        else:
            messagebox.showinfo('提示', '到达作业页面后请手动选择您要刷的作业...')

    def save(self):
        account = self.config.get_account()
        if not self._validate():
            return
        account['user_notice'] = 'False'
        account['browser'] = self.browser_entry.get()
        account['driver_path'] = self.browser_driver_entry.get() if \
            self.browser_entry.get() != '不指定浏览器' else ''
        account['phone_number'] = self.phone_number_entry.get().replace('\n', '')
        account['password'] = self.password_entry.get().replace('\n', '')
        courses = [self.cour_entry.get().replace('\n', '')]
        courses += [e.get() for e, _, _, _ in self.dynamic_rows if e.get().replace('\n', '')]
        self.all_courses = courses
        account['cour'] = courses
        account['choice'] = self.question_entry.get()
        account['after_finish_question'] = self.after_finish_question_entry.get()
        account['video_title_choice'] = self.vido_question_entry.get()
        account['discussion_choice'] = self.discussion_entry.get()
        account['API'] = self.API_entry.get()
        account['speed'] = self.speed_entry.get()
        account['homework'] = self.homework_entry.get()
        account['task_type'] = '章节' if self.radio_var.get() == 1 else '作业'
        account['font_type'] = self.font_entry.get()
        account['font_size'] = self.size_entry.get()
        account['pass_face'] = self.pass_face_check.get()
        account['multi_device'] = self.multi_device_check.get()
        account['pass_vido'] = self.pass_vido_check.get()
        account['lock_screen'] = self.lock_screen_check.get()
        account['radio_var'] = self.radio_var.get()

        if messagebox.askokcancel('确认保存', '你确定要保存吗？\n(使用DeepSeek可支持全题型作答)'):
            if self.config.save_account(account):
                self.config.save_courses(account['phone_number'], courses)
                messagebox.showinfo('', '保存成功')
                self.change_font()
                self.change_text_box(self.all_courses,self.multi_device_check.get())
                self.root.update()
            else:
                messagebox.showerror('警告', '保存失败，请以管理员权限运行')

    def _validate(self):
        checks = [
            (self.browser_entry.get(), '请选择浏览器'),
            (self.browser_driver_entry.get(), '请填写驱动地址'),
            (self.phone_number_entry.get(), '请填写手机号'),
            (self.password_entry.get(), '请填写密码'),
            (self.cour_entry.get(), '请填写课程名称'),
            (self.question_entry.get(), '请完成章节测验刷题设置'),
        ]
        for val, msg in checks:
            if not val:
                messagebox.showerror('警告', msg)
                return False
        if self.after_finish_question_entry.get() == '' and self.question_entry.get() == 'DeepSeek AI':
            messagebox.showerror('警告', '请完成答完题后的设置')
            return False
        if self.radio_var.get() == 1:
            if not self.vido_question_entry.get():
                messagebox.showerror('警告', '请完成视频题目设置')
                return False
            if not self.discussion_entry.get():
                messagebox.showerror('警告', '请完成讨论设置')
                return False
            if not self.speed_entry.get():
                messagebox.showerror('警告', '请填写倍数')
                return False
        if self.radio_var.get() == 2 and not self.homework_entry.get():
            messagebox.showerror('警告', '请填写作业选择形式')
            return False
        api = self.API_entry.get()
        if any(e.get() == 'DeepSeek AI' for e in
               [self.question_entry, self.vido_question_entry, self.discussion_entry]):
            if not api:
                messagebox.showerror('警告', '请填写DeepSeek API')
                return False
        return True

    def load_data(self, data):
        self.data = data
        account = self.config.get_account()
        self.cour_entry.configure(values=tuple(data))
        self.browser_entry.set(account.get('browser', ''))
        if account.get('browser') != '不指定浏览器':
            self.browser_driver_entry.insert(0, account.get('driver_path', ''))
        else:
            self.browser_driver_entry.insert(0, '无需填写')
            self.browser_driver_entry.configure(state=tk.DISABLED)
        self.speed_entry.set(account.get('speed', ''))
        self.phone_number_entry.insert(0, account.get('phone_number', ''))
        self.password_entry.insert(0, account.get('password', ''))
        self.cour_entry.set(account.get('cour', [''])[0])
        self.question_entry.set(account.get('choice', ''))
        self.after_finish_question_entry.set(account.get('after_finish_question', ''))
        self.timer_start_time = account.get('timer_start', '04:00:00')
        self.timer_end_time = account.get('timer_end', '03:00:00')
        if account.get('video_title_choice', ''):
            self.vido_question_entry.set(account['video_title_choice'])
        self.discussion_entry.set(account.get('discussion_choice', ''))
        self.homework_entry.set(account.get('homework', ''))
        self.radio_var.set(account.get('radio_var', 1))
        for attr, key in [('pass_face_check', 'pass_face'), ('multi_device_check', 'multi_device'),
                          ('pass_vido_check', 'pass_vido'), ('lock_screen_check', 'lock_screen'),
                          ('timer_check', 'timer_active')]:
            getattr(self, attr).select() if account.get(key, 0) else getattr(self, attr).deselect()
        try:
            self.API_entry.insert(0, account.get('API', ''))
            self.font_entry.set(account.get('font_type', ''))
            self.size_entry.set(account.get('font_size', ''))
            self.change_font()
        except:
            pass
        for name in account.get('cour', [])[1:]:
            self.add_course(name)

    @property
    def comboboxes(self):
        return [self.speed_entry, self.question_entry, self.cour_entry,
                self.size_entry, self.homework_entry, self.font_entry,
                self.browser_entry, self.vido_question_entry,
                self.discussion_entry, self.after_finish_question_entry]

    @property
    def switches(self):
        return [self.topmost_check, self.pass_face_check,self.timer_check,
                self.multi_device_check, self.lock_screen_check, self.pass_vido_check]

    @property
    def buttons(self):
        return [self.save_button, self.open_file_button]