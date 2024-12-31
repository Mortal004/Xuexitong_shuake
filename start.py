import json
import os
import signal
from datetime import datetime
import re
import threading
import tkinter as tk
import subprocess

from PIL import Image, ImageTk
from colorama import Fore
from tkinter import ttk, font, messagebox, filedialog



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
        self.thread = None
        self.process = None
        self.font = ("Helvetica", 12)
        self.cour = None
        self.password = None
        self.phone_number = None
        self.account_info = None

        self.root = tk.Tk()
        self.root.geometry("+1050+20")  # 设置窗口大小
        self.root.title('学习通刷课（exe)')
        self.root.attributes('-topmost',False)
        self.score_frame = tk.Frame(self.root)
        self.main_frame = tk.Frame(self.root)
        self.error_frame= tk.Frame(self.root)
        self.vido_frame = tk.Frame(self.root)
        self.set_frame = tk.Frame(self.root)
        self.help_frame = tk.Frame(self.root)
        self.money_frame = tk.Frame(self.root)
        # self.root.resizable(False, False)  # 禁止用户调整窗口大小
         # 使用ico格式的图标文件
        self.root.iconbitmap(r'task\img\xuexitong1 .ico')
        #透明度
        self.root.attributes('-alpha',1)
        # 设置背景颜色
        # self.root.config(bg='black')
        # self.score_frame.configure(bg='black')
        # self.main_frame.configure(bg='black')
        # self.error_frame.configure(bg='black')
        # self.vido_frame.configure(bg='black')

        # 创建菜单栏
        menu_bar = tk.Menu(self.root,bg='black',fg='white')
        # 创建文件菜单并添加选项
        menu_bar.add_command(label='  主页  ',command=self.show_main,font= ("Helvetica", 12))
        menu_bar.add_command(label='  刷课日志  ', command=self.show_vido)
        menu_bar.add_command(label='  测试成绩  ', command=self.show_score)
        menu_bar.add_command(label='  报错日志  ', command=self.show_error)
        menu_bar.add_command(label=' 设置 ', command=self.show_set)
        menu_bar.add_command(label=' 帮助 ', command=self.show_help)
        menu_bar.add_command(label='赞助作者', command=self.show_money)

        # ---------------- 主页 ----------------
        # 创建按钮1
        self.button1 = tk.Button(self.main_frame, text="启动程序",bg= 'skyblue',command=self.run_program,font=self.font)
        # self.button1.config(image=self.img)
        self.button1.grid(row=0, column=0)
        # 创建按钮2
        self.button2 = tk.Button(self.main_frame, text="关闭程序",command=self.close,font=self.font)
        self.button2.grid(row=0, column=1)
        # 配置按钮框架的列权重，使按钮居中
        self.main_frame.columnconfigure((0,1), weight=1)
        self.main_frame.rowconfigure((0,1), weight=1)
        # 创建只读文本框#202022
        self.text_box = tk.Text(self.main_frame,bg='white',height=27,width=55,font=self.font)
        self.text_box.insert(tk.INSERT,'WELCOME TO 学习通刷课（exe) ！！！\n请先进入设置页面填写信息！！！')
        self.text_box.tag_configure("center", justify='center')
        self.text_box.tag_add("center", "1.0", "end")
        self.text_box.tag_configure("red", foreground="red")
        self.text_box.tag_add("red", "1.0", "end")
        self.text_box.config( state=tk.DISABLED)
        self.text_box.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky=tk.W+tk.E+tk.N+tk.S)

        # ---------------- 刷课记录 ----------------
        # 下拉选项框（包含可输入部分）
        self.course_vido_entry = ttk.Combobox(self.vido_frame,font=self.font)
        self.course_vido_entry['state'] = 'normal'
        self.course_name = self.course_vido_entry.get()
        self.course_vido_entry.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W + tk.E)  # 使用 sticky 参数使组件填满整个单元格
        # 按钮
        button = tk.Button(self.vido_frame, text="查询", command=self.show_vido,font=self.font)
        button.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)  # 使用 sticky 参数使组件填满整个单元格
        # 配置按钮框架的列权重，使按钮居中
        self.score_frame.rowconfigure(0, weight=1)
        # self.score_frame.columnconfigure(1, weight=1)
        #创建只读文本框
        self.vido_text = tk.Text(self.vido_frame, height=27, width=55,font=self.font)
        self.vido_text.config(state=tk.DISABLED)
        self.vido_text.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky=tk.W+tk.E+tk.N+tk.S)

        # ---------------- 成绩日志 ----------------
        # 下拉选项框（包含可输入部分）
        self.course_score_entry = ttk.Combobox(self.score_frame,font=self.font)
        self.course_score_entry['state'] = 'normal'
        self.course_name=self.course_score_entry.get()
        self.course_score_entry.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W+tk.E)  # 使用 sticky 参数使组件填满整个单元格
        # 按钮
        button = tk.Button(self.score_frame, text="查询", command=self.show_score,font=self.font)
        button.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)  # 使用 sticky 参数使组件填满整个单元格
        # 配置按钮框架的列权重，使按钮居中
        self.score_frame.rowconfigure(0, weight=1)
        # self.score_frame.columnconfigure(1, weight=1)
        # 创建只读文本框
        self.score_txt = tk.Text(self.score_frame,height=27,width=55,font=self.font)
        self.score_txt.config(state=tk.DISABLED)
        self.score_txt.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky=tk.W+tk.E+tk.N+tk.S)  # 使用 sticky 参数使组件填满整个单元格

        #error_frame页面
        self.error_text = tk.Text(self.error_frame, height=30, width=57,font=self.font)
        self.error_text.config(state=tk.DISABLED)
        self.error_text.grid()

        # ---------------- 设置 ----------------
        #配置设置
        self.configuration_set_frame=tk. LabelFrame(self.set_frame, text="配置设置：",font=self.font,padx=10, pady=10)
        self.configuration_set_frame.grid(row=0,column=0,sticky="nsew", padx=5, pady=5)
        # Chrome driver
        self.chrome_driver_label = tk.Label(self.configuration_set_frame, text="谷歌驱动:",font=self.font)
        self.chrome_driver_label.grid(row=1, column=1, padx=5, pady=10, sticky=tk.W)
        self.chrome_driver_entry = tk.Entry(self.configuration_set_frame,width=43)
        self.chrome_driver_entry.grid(row=1, column=2, padx=5, pady=10, sticky=tk.W)
        self.open_file_button = tk.Button(self.configuration_set_frame, text="选择文件", command=self.select_file1)
        self.open_file_button.grid(row=2, column=2, sticky=tk.W)
        # 搜题插件
        self.extension_label = tk.Label(self.configuration_set_frame, text="搜题插件:",font=self.font)
        self.extension_label.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        self.extension_entry = tk.Entry(self.configuration_set_frame,width=43)
        self.extension_entry.grid(row=3, column=2, padx=5, pady=5, sticky=tk.W)
        self.select_file_button = tk.Button(self.configuration_set_frame, text="选择文件", command=self.select_file2)
        self.select_file_button.grid(row=4, column=2,sticky=tk.W)

        #界面设置
        self.frame_set_frame= tk. LabelFrame(self.set_frame, text="界面设置：",font=self.font,padx=10, pady=10)
        self.frame_set_frame.grid(row=1, column=0,  sticky='nsew', padx=5, pady=5)
        #字体设置
        self.font_label = tk.Label(self.frame_set_frame, text="字体设置：", font=self.font)
        self.font_label.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        self.font_entry = ttk.Combobox(self.frame_set_frame, values= font.families(),font=self.font)
        self.font_entry.grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        # 大小设置
        self.size=['9','10','11','12','13','14','15','16']
        self.size_label = tk.Label(self.frame_set_frame, text="大小设置：", font=self.font)
        self.size_label.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        self.size_entry = ttk.Combobox(self.frame_set_frame, values=self.size, font=self.font)
        self.size_entry.grid(row=2, column=2, padx=5, pady=5, sticky=tk.W)
        # 窗口置顶勾选框
        self.topmost_var = tk.BooleanVar(value=False)
        self.topmost_check = ttk.Checkbutton(
            self.frame_set_frame, text='窗口始终置顶', variable=self.topmost_var,
            command=self.toggle_topmost, style='TCheckbutton')
        self.topmost_check.grid(row=3,column=1,padx=5,columnspan=2)

        #信息设置
        self.message_set_frame = tk .LabelFrame(self.set_frame, text="信息设置：",font=self.font,padx=10, pady=10)
        self.message_set_frame.grid(row=2,  column=0,  sticky='nsew', padx=5, pady=5)
        # 账户：输入框
        self.phone_number_label = tk.Label(self.message_set_frame, text="账号:", font=self.font)
        self.phone_number_label.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        self.phone_number_entry = tk.Entry(self.message_set_frame, font=self.font)
        self.phone_number_entry.grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        # 密码:输入框
        self.password_label = tk.Label(self.message_set_frame, text="密码:", font=self.font)
        self.password_label.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        self.password_entry = tk.Entry(self.message_set_frame, font=self.font,show='*')
        self.password_entry.grid(row=2, column=2, padx=5, pady=5, sticky=tk.W)
        # 输入框：课程
        self.cour_label = tk.Label(self.message_set_frame, text="课程名称:", font=self.font)
        self.cour_label.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        self.cour_entry = ttk.Combobox(self.message_set_frame, font=self.font)
        self.cour_entry['state'] = 'normal'
        self.cour_entry.grid(row=3, column=2, padx=5, pady=5, sticky=tk.W)
        # 刷题：输入框
        self.question_label = tk.Label(self.message_set_frame, text="是否做题:", font=self.font)
        self.question_label.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)
        self.question_options = ["是", "否"]
        self.question_entry = ttk.Combobox(self.message_set_frame, values=self.question_options, font=self.font)
        # self.question_entry['state'] = 'readonly'
        self.question_entry.grid(row=4, column=2, padx=5, pady=5, sticky=tk.W)

        # 创建按钮
        self.save_button = tk.Button(self.set_frame, text="保存", command=self.save, font=self.font)
        self.save_button.grid(row=3, column=0, padx=10, pady=10)
        #设置网格权重
        self.set_frame.rowconfigure(3,weight=1)
        self.frame_set_frame.rowconfigure(3,weight=1)

        #帮助页面
        with open('Help.txt', 'r', encoding='utf-8') as f:
            self.text = f.read()
        self.help_txt = tk.Text(self.help_frame,height=27,width=60,font=self.font)
        self.help_txt.grid()
        self.help_txt.insert(tk.END, self.text)
        self.help_txt.config(state=tk.DISABLED)

        #赞助页面
        self.label1 = tk.Label(self.money_frame, text="如果对你有帮助，欢迎给我打赏,你们的支持就是我更新的最大动力\n(PS:会优先解决打赏的人出现的问题哦！)", font=self.font)
        self.label1.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky=tk.W)
        # 加载图片
        self.image = Image.open(r"task\img\money.jpg")  # 替换为你的图片路径
        self.photo = ImageTk.PhotoImage(self.image)

        # 创建标签并显示图片
        self.label = tk.Label(self.money_frame, image=self.photo)
        self.label.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky=tk.W)

        # 当前时间显示
        self.time_label = tk.Label(self.root,text="")
        self.time_label.grid(row=0, column=0, columnspan=2, padx=10, pady=1, sticky=tk.W)
        self.main_frame.grid()
        self.root.config(menu=menu_bar)
        # 更新时间显示
        self.update_time()
        self.load_data()

    def toggle_topmost(self):
        """切换窗口始终置顶属性"""
        self.root.attributes("-topmost", self.topmost_var.get())


    def show_main(self):
        self.main_frame.grid()
        self.error_frame.grid_forget()
        self.score_frame.grid_forget()
        self.vido_frame.grid_forget()
        self.set_frame.grid_forget()
        self.help_frame.grid_forget()
        self.money_frame.grid_forget()

    def show_vido(self):
        self.vido_text.config(state=tk.NORMAL)
        try:
            with open(f'《{self.course_vido_entry.get()}》的刷课记录.txt', 'r', encoding='utf-8') as f:
                content = f.read()
                self.vido_text.delete('1.0', tk.END)
                self.vido_text.insert(tk.END, content)
        except FileNotFoundError:
            self.vido_text.delete('1.0', tk.END)
            self.vido_text.insert(tk.END, f'暂未查询到《{self.course_vido_entry.get()}》的刷课记录')
        self.vido_frame.grid()
        self.error_frame.grid_forget()
        self.score_frame.grid_forget()
        self.main_frame.grid_forget()
        self.vido_text.config(state=tk.DISABLED)
        self.set_frame.grid_forget()
        self.help_frame.grid_forget()
        self.money_frame.grid_forget()

    def show_score(self):
        self.score_txt.config(state=tk.NORMAL)
        try:
            with open(f'《{self.course_score_entry.get()}》的成绩记录.txt', 'r', encoding='utf-8') as f:
                content = f.read()
                self.score_txt.delete('1.0', tk.END)
                self.score_txt.insert(tk.END, content)
        except FileNotFoundError:
            self.score_txt.delete('1.0', tk.END)
            self.score_txt.insert(tk.END, f'暂未查询到《{self.course_score_entry.get()}》的成绩记录')
        self.score_frame.grid()
        self.error_frame.grid_forget()
        self.main_frame.grid_forget()
        self.vido_frame.grid_forget()
        self.score_txt.config(state=tk.DISABLED)
        self.set_frame.grid_forget()
        self.help_frame.grid_forget()
        self.money_frame.grid_forget()

    def show_error(self):
        try:
            self.error_text.config(state=tk.NORMAL)
            with open('error.log', 'r',encoding='utf-8') as f:
                content = f.read()
                self.error_text.delete('1.0', tk.END)
                self.error_text.insert(tk.END, content)
        except FileNotFoundError:
            self.error_text.delete('1.0', tk.END)
            self.error_text.insert(tk.END, '暂无报错记录')
        self.error_frame.grid()
        self.score_frame.grid_forget()
        self.main_frame.grid_forget()
        self.vido_frame.grid_forget()
        self.error_text.config(state=tk.DISABLED)
        self.set_frame.grid_forget()
        self.help_frame.grid_forget()
        self.money_frame.grid_forget()

    def show_set(self):
        self.set_frame.grid()
        self.error_frame.grid_forget()
        self.score_frame.grid_forget()
        self.main_frame.grid_forget()
        self.vido_frame.grid_forget()
        self.help_frame.grid_forget()
        self.money_frame.grid_forget()

    def show_money(self):
        self.money_frame.grid()
        self.error_frame.grid_forget()
        self.score_frame.grid_forget()
        self.main_frame.grid_forget()
        self.vido_frame.grid_forget()
        self.set_frame.grid_forget()
        self.help_frame.grid_forget()

    def select_file1(self):
        file_path = filedialog.askopenfilename(title="选择文件", filetypes=[("", "*.exe")])
        if file_path:
            self.chrome_driver_entry.delete(0, tk.END)
            self.chrome_driver_entry.insert(tk.END,file_path)

    def select_file2(self):
        file_path = filedialog.askopenfilename(title="选择文件", filetypes=[("", "*.crx")])
        if file_path:
            self.extension_entry.delete(0,tk.END)
            self.extension_entry.insert(tk.END,file_path)

    def show_help(self):
        self.help_frame.grid()
        self.set_frame.grid_forget()
        self.error_frame.grid_forget()
        self.score_frame.grid_forget()
        self.main_frame.grid_forget()
        self.vido_frame.grid_forget()
        self.money_frame.grid_forget()

    def run_program(self):
        """
        运行 main.py 程序，并将其输出实时显示在 GUI 的文本框中。
        """
        # 确保文本框可编辑
        self.text_box.config(state=tk.NORMAL)
        # 清空文本框内容
        self.text_box.delete('1.0', tk.END)
        def read_output():
            """
            读取 main.py 程序的输出，并将其显示在文本框中。
            """
            # 启动 main.py 程序
            self.process = subprocess.Popen(['python','main.py'],
                                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            color_tag = None
            while True:
                output = self.process.stdout.readline()
                if self.process is None:
                    break
                if output == b'' and self.process.poll() is not None:
                    break
                if output:
                    decoded_output = output.decode()

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
            self.text_box.config(state=tk.DISABLED)

        # 使用线程来运行读取输出的函数，避免阻塞主事件循环
        self.thread = threading.Thread(target=read_output)
        self.thread.start()

    def close(self):

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
        self.time_label.config(text=f"当前时间: {current_time}")
        self.root.after(1000, self.update_time)  # 每秒更新一次

    def change_font(self):
        self.font = (self.font_entry.get(), self.size_entry.get())
        def update_font(widget):
            if isinstance(widget,( tk.Label, tk.Button, tk.Text,ttk.Combobox, tk.Entry, tk.LabelFrame)):
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
                with open('course_name.json', 'r') as f:
                    data = json.load(f)
            except FileNotFoundError:
                pass
            if content not in data:
                data.append(content)
                with open('course_name.json', 'w' , encoding='utf-8')as f:
                    json.dump(data, f)

    def save(self):
        try:
            with open('account_info.json', 'r', encoding='utf-8') as f:
                self.account_info = json.load(f)
        except FileNotFoundError:
            self.account_info = {}
        if self.chrome_driver_entry.get()=='':
            tk.messagebox.showerror('警告', message='请填写谷歌驱动的地址')
            return False
        else:
            self.account_info['driver_path']=self.chrome_driver_entry.get()
        if self.extension_entry.get()=='':
            tk.messagebox.showerror('警告', message='请填写搜题插件的地址')
            return False
        else:
            self.account_info['extension_path']=self.extension_entry.get()
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
        if self.question_entry.get() == '是' or self.question_entry.get() == '否':
            self.account_info['choice'] = self.question_entry.get()
        else:
            tk.messagebox.showerror('警告', message='请选择是否做题')
            return False
        self.account_info['font_type']=self.font_entry.get()
        self.account_info['font_size']=self.size_entry.get()
        if self.question_entry.get()=='是':
            self.result = tk.messagebox.askokcancel('确认保存', '你确定要保存吗？\n(注意：搜题只能搜索选择题和判断题)')
        elif self.question_entry.get() == '否':
            self.result = tk.messagebox.askokcancel('确认保存', '你确定要保存吗？')
        if self.result:
            tk.messagebox.showinfo('', '保存成功')
            with open('account_info.json', 'w', encoding='utf-8') as f:
                json.dump(self.account_info, f)
            self.save_course()
            self.change_font()
            self.root.update()

    def load_data(self):
        try:
            with open('course_name.json', 'r') as f:
                data = json.load(f)
                if data:
                    self.course_score_entry['values'] = tuple(data)
                    self.course_vido_entry['values'] = tuple(data)
                    self.cour_entry['values'] = tuple(data)

            with open('account_info.json', 'r', encoding='utf-8') as fil:
                self.account_info = json.load(fil)
                self.course_score_entry.insert(0, self.account_info['cour'])
                self.course_vido_entry.insert(0, self.account_info['cour'])
                self.phone_number_entry.insert(0, self.account_info['phone_number'])
                self.password_entry.insert(0, self.account_info['password'])
                self.cour_entry.insert(0, self.account_info['cour'])
                self.question_entry.insert(0, self.account_info['choice'])
                self.chrome_driver_entry.insert(0,self.account_info['driver_path'])
                self.extension_entry.insert(0,self.account_info['extension_path'])
                try:
                    self.font_entry.insert(0, self.account_info['font_type'])
                    self.size_entry.insert(0,self.account_info['font_size'])
                    self.change_font()
                except:
                    pass
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    client = Start()
    client.root.mainloop()

