"""定时刷课设置窗口"""
import re
import tkinter as tk
import customtkinter as ctk


class TimerWindow:
    def __init__(self, root, on_set, on_cancel, get_font, get_colors):
        self.root = root
        self.on_set = on_set
        self.on_cancel = on_cancel
        self.get_font = get_font
        self.get_colors = get_colors

    def open(self, start_time, end_time):
        colors = self.get_colors()
        font = self.get_font()

        win = ctk.CTkToplevel(self.root)
        win.title("⏰ 定时刷课设置")
        win.geometry("350x200")
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()

        ctk.CTkLabel(win, text="开始时间 (HH:MM:SS):", font=font).grid(
            row=0, column=0, padx=10, pady=10, sticky="w")
        start_entry = ctk.CTkEntry(win, width=120, font=font)
        start_entry.grid(row=0, column=1, padx=10, pady=10)
        start_entry.insert(0, start_time)

        ctk.CTkLabel(win, text="结束时间 (HH:MM:SS):", font=font).grid(
            row=1, column=0, padx=10, pady=10, sticky="w")
        end_entry = ctk.CTkEntry(win, width=120, font=font)
        end_entry.grid(row=1, column=1, padx=10, pady=10)
        end_entry.insert(0, end_time)
        win.protocol("WM_DELETE_WINDOW", lambda :self._set(win, start_entry.get().strip(), end_entry.get().strip()))

        ctk.CTkButton(win, text="开启定时", fg_color=colors[0],
                      hover_color=colors[2], font=font,
                      command=lambda: self._set(win, start_entry.get().strip(),
                                                end_entry.get().strip())
                      ).grid(row=2, column=0,columnspan=2, padx=10, pady=20)

        # ctk.CTkButton(win, text="禁用定时", fg_color=colors[0],
        #               hover_color=colors[2], font=font,
        #               command=lambda: self._cancel(win)
        #               ).grid(row=2, column=1, padx=10, pady=20)

    def _set(self, window, start_str, end_str):
        pattern = r"^([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$"
        if not re.match(pattern, start_str) or not re.match(pattern, end_str):
            tk.messagebox.showerror("错误", "时间格式不正确，请输入 HH:MM:SS 格式")
            return
        sh, sm, ss = map(int, start_str.split(":"))
        eh, em, es = map(int, end_str.split(":"))
        if sh * 3600 + sm * 60 + ss == eh * 3600 + em * 60 + es:
            tk.messagebox.showerror("错误", "结束时间不能与开始时间相同")
            return
        self.on_set(start_str, end_str)
        window.destroy()

    def cancel(self):
        self.on_cancel()
        # window.destroy()
