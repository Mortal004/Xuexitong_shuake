"""用户须知弹窗"""
import tkinter as tk

NOTICE_TEXT = """欢迎使用学习通刷课程序！
    【重要声明】
    1. 本人从未建过QQ群，也没在B站上发布过任何视频，如果你是在这两个
    平台上下载的脚本，请尽快删除，以避免电脑中病毒，下载正版请联系
    邮箱2022865286@qq.com。
    2. 本软件仅供个人学习交流使用，不得用于任何商业用途。
    3. 使用本软件产生的任何后果由使用者自行承担，开发者不承担任何责任。
    4. 请遵守学校相关规定，合理使用本软件辅助学习。
    5. 不得恶意利用本软件进行任何违规行为。
    6. 开发者保留对本软件的最终解释权。
    【使用说明】
    1. 建议在稳定的网络环境下使用本软件。
    2. 如遇到问题，请查看用户须知文档或联系作者。
    3. 请勿频繁使用高速倍速播放功能，以免触发平台检测机制。
    
    请您仔细阅读以上内容，使用本软件即表示您同意遵守上述条款。"""

class UserNotice:
    def __init__(self, root, on_confirm, on_cancel):
        self.root = root
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
        self.remaining_time = 10

    def show(self):
        notice_window = tk.Toplevel(self.root)
        notice_window.title("用户须知")
        notice_window.resizable(False, False)
        notice_window.transient(self.root)
        notice_window.grab_set()
        notice_window.wm_attributes("-topmost", True)

        text_widget = tk.Text(notice_window, wrap=tk.WORD,
                              font=("微软雅黑", 12), height=16, width=65)
        text_widget.insert(tk.END, NOTICE_TEXT)
        text_widget.config(state=tk.DISABLED)
        text_widget.grid(row=0, column=0, padx=10, pady=10)

        button_frame = tk.Frame(notice_window)
        button_frame.grid(row=1, column=0, pady=10)

        self.confirm_button = tk.Button(
            button_frame, text=f"确认 ({self.remaining_time}s)",
            width=7, height=1, font=("微软雅黑", 13),
            state=tk.DISABLED, command=lambda: self._confirm(notice_window))
        cancel_button = tk.Button(
            button_frame, width=6, height=1, text="取消",
            command=lambda: self._cancel(notice_window),
            font=("微软雅黑", 13))

        self.confirm_button.pack(side=tk.LEFT, padx=10)
        cancel_button.pack(side=tk.LEFT, padx=10)

        self._countdown(notice_window)

        notice_window.update_idletasks()
        x = (notice_window.winfo_screenwidth() // 2) - (notice_window.winfo_width() // 2)
        y = (notice_window.winfo_screenheight() // 2) - (notice_window.winfo_height() // 2)
        notice_window.geometry(f"+{x}+{y}")
        notice_window.protocol("WM_DELETE_WINDOW", lambda: None)

    def _countdown(self, window):
        if self.remaining_time > 0:
            self.confirm_button.config(text=f"确认 ({self.remaining_time}s)")
            self.remaining_time -= 1
            window.after(1000, lambda: self._countdown(window))
        else:
            self.confirm_button.config(text="确认", state=tk.NORMAL)

    def _confirm(self, window):
        window.destroy()
        self.on_confirm()

    def _cancel(self, window):
        window.destroy()
        self.on_cancel()