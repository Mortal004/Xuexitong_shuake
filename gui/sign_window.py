from __future__ import annotations
import sys
import threading
import tkinter as tk
import customtkinter as ctk

import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from task.xxt import constants, login as login_mod, monitor, storage  # noqa: E402
sign_txt = None


def bootstrap( phone: str = None, password: str = None):
    """获取可用会话: 优先用本地保存的信息, 否则提示输入"""
    client = login_mod.restore_client(sign_text=sign_txt)
    if client is not None:
        storage.log("已使用本地保存的登录信息(%s), 无需重新输入账号密码"
                    % (client.name or client.uid),sign_text=sign_txt)
        return client


    while True:
        client, msg = login_mod.do_login(phone, password)
        if client is not None:
            storage.log(msg,sign_text=sign_txt)
            storage.log("登录信息已保存到 data/config.json, 下次启动免输入",sign_text=sign_txt)
            return client
        storage.log("登录失败: %s" % msg,sign_text=sign_txt)
        if not input("重新输入? (回车继续 / 输入 q 退出): ").strip().lower() == "q":
            continue
        return None


def main(phone: str = None, password: str = None, stop_event=None) -> int:
    parser = argparse.ArgumentParser(description="学习通自动签到(精简版: 普通/位置)")
    parser.add_argument("--interval", type=int, default=constants.CHECK_INTERVAL,
                        help="检查间隔秒数, 默认 7")
    parser.add_argument("--once", action="store_true", help="只检查一轮")
    parser.add_argument("--workers", type=int, default=monitor.DEFAULT_WORKERS,
                        help="并发读取课程的线程数, 默认 8(设 1 为串行)")
    parser.add_argument("--relogin", action="store_true", help="忽略本地信息, 重新登录")
    args = parser.parse_args()

    client = bootstrap(phone=phone, password=password)
    if client is None:
        storage.log("未获得有效登录, 退出",sign_text=sign_txt)
        return 1

    if args.once:
        started = time.time()
        handled = monitor.scan_and_sign_once(client, workers=args.workers)
        storage.log("本轮完成 %d 个签到, 耗时 %.1f 秒" % (len(handled), time.time() - started),sign_text=sign_txt)
        return 0

    try:
        monitor.monitor(client, interval=args.interval, workers=args.workers, stop_event=stop_event,sign_text=sign_txt)
    except KeyboardInterrupt:
        storage.log("已手动停止",sign_text=sign_txt)
    return 0
def start_sign_monitor(account, stop_event=None,sign_text=None):
    global sign_txt
    sign_txt = sign_text
    phone = account.get("phone_number", "")
    password = account.get("password", "")
    main(phone=phone, password=password, stop_event=stop_event)


class SignWindow:
    def __init__(self, master, account_info, font, auto_sign_btn, button_color, button_hover_color):
        self.master = master
        self.account_info = account_info
        self.stop_event = threading.Event()
        self.monitor_thread = None
        self._orig_stdout = sys.stdout
        self.auto_sign_btn = auto_sign_btn
        self.auto_sign_btn.configure(state=tk.DISABLED)
        self.window = ctk.CTkToplevel(master)
        self.window.title("自动签到监控")
        self.window.geometry("350x250")
        self.window.resizable(True, True)
        self.window.after(100, self.window.lift)
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        self.btn_frame = ctk.CTkFrame(self.window, fg_color='transparent')
        self.btn_frame.pack(fill=tk.X, padx=10, pady=(10, 0))

        self.sign_text = ctk.CTkTextbox(self.window, font=font,border_width=1)
        self.sign_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.hint_label = ctk.CTkLabel(self.btn_frame, font=ctk.CTkFont(size=11),
                                        text="提示：暂时只能自动完成常规签到和位置签到，其余的需手动签到",
                                        fg_color='transparent', text_color='gray')
        self.hint_label.pack(side=tk.TOP, anchor=tk.W, pady=(0, 5))
        self.start_btn = ctk.CTkButton(self.btn_frame, text="▶ 启动自动签到", font=font,
                                        fg_color=button_color,
                                        hover_color=button_hover_color,
                                        command=self.start_monitor)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ctk.CTkButton(self.btn_frame, text="■ 关闭自动签到", font=font,
                                       fg_color="#F87171",
                                       hover_color="#EF4444",
                                       command=self.stop_monitor)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

    def start_monitor(self):
        self.stop_event.clear()
        self.sign_text.delete('1.0', tk.END)

        def run():
            try:
                start_sign_monitor(self.account_info, self.stop_event, self.sign_text)
            except Exception as e:
                self.sign_text.after(0, self.sign_text.insert, tk.END, f"[错误] 监控启动失败: {e}\n")
                self.sign_text.after(0, self.sign_text.see, tk.END)
            finally:
                sys.stdout = self._orig_stdout

        self.monitor_thread = threading.Thread(target=run, daemon=True)
        self.monitor_thread.start()
        self.start_btn.configure(state=tk.DISABLED)
        self.stop_btn.configure(state=tk.NORMAL)

    def stop_monitor(self):
        self.stop_event.set()
        sys.stdout = self._orig_stdout
        self.sign_text.insert(tk.END, "自动签到已关闭\n")
        self.stop_btn.configure(state=tk.DISABLED)
        self.start_btn.configure(state=tk.NORMAL)

    def on_close(self):
        self.stop_monitor()
        self.window.destroy()
        self.auto_sign_btn.configure(state=tk.NORMAL)