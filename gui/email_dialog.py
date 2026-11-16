# -*- coding: utf-8 -*-
"""
邮箱通知配置弹窗

用法::

    dlg = EmailNotifyDialog(root, config_manager, font, colors)
    if dlg.show():        # 用户测试/保存成功
        ...

特点：
  * 选择邮箱服务商后自动带出 SMTP 参数；
  * 授权码输入框旁边就是「教程」按钮，按服务商跳转到对应帮助页；
  * 「测试并保存」会真的发一封测试邮件，成功才落盘；
  * 也提供「仅保存」，方便暂时没有网络时先存配置。
"""
from __future__ import annotations

import tkinter as tk
import webbrowser

import customtkinter as ctk

from task.tool import mailer


class EmailNotifyDialog:
    def __init__(self, master, config, font, colors, on_saved=None):
        self.master = master
        self.config = config
        self.font = font
        self.colors = colors or ['#1E88E5', '#E3F2FD', '#81AED1']
        self.on_saved = on_saved
        self.result = False
        self.win = None
        self._settings = {}

    # ------------------------------------------------------------ 入口
    def show(self):
        try:
            self._settings = mailer.load_settings()
        except Exception:
            self._settings = {}
        self._build()
        try:
            self.win.wait_window()
        except Exception:
            pass
        return self.result

    # ------------------------------------------------------------ 构建
    def _build(self):
        accent, _bg, accent_hover = self.colors[0], self.colors[1], self.colors[2]

        self.win = ctk.CTkToplevel(self.master)
        self.win.title('邮箱通知设置')
        self.win.geometry('560x440')
        self.win.resizable(False, False)
        self.win.transient(self.master)
        self.win.grab_set()
        self.win.after(120, self.win.lift)
        self.win.protocol('WM_DELETE_WINDOW', self.win.destroy)

        body = ctk.CTkFrame(self.win, fg_color='transparent')
        body.pack(fill=tk.BOTH, expand=True, padx=20, pady=16)
        body.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(body, text='📧  邮箱通知', font=('Microsoft YaHei', 17, 'bold'),
                     anchor='w').grid(row=0, column=0, columnspan=3, sticky='w', pady=(0, 4))
        ctk.CTkLabel(body, text='开启后：开始刷课、完成一个章节、程序报错时都会发邮件提醒。',
                     font=('Microsoft YaHei', 11), text_color='#6B7280',
                     anchor='w', justify='left', wraplength=500).grid(
            row=1, column=0, columnspan=3, sticky='w', pady=(0, 12))

        # 服务商
        ctk.CTkLabel(body, text='邮箱类型:', font=self.font).grid(
            row=2, column=0, sticky='w', pady=6, padx=(0, 8))
        self.provider_entry = ctk.CTkComboBox(
            body, values=mailer.provider_names(), state='readonly', font=self.font,
            corner_radius=6, command=self._on_provider_changed)
        self.provider_entry.grid(row=2, column=1, columnspan=2, sticky='ew', pady=6)

        self.hint_label = ctk.CTkLabel(
            body, text='', font=('Microsoft YaHei', 11), text_color='#6B7280',
            anchor='w', justify='left', wraplength=500)
        self.hint_label.grid(row=3, column=0, columnspan=3, sticky='w', pady=(0, 10))

        # 邮箱地址
        ctk.CTkLabel(body, text='邮箱地址:', font=self.font).grid(
            row=4, column=0, sticky='w', pady=6, padx=(0, 8))
        self.account_entry = ctk.CTkEntry(body, font=self.font, corner_radius=6,
                                          placeholder_text='例如 xxxx@qq.com')
        self.account_entry.grid(row=4, column=1, columnspan=2, sticky='ew', pady=6)

        # 授权码 + 教程按钮
        ctk.CTkLabel(body, text='授权码:', font=self.font).grid(
            row=5, column=0, sticky='w', pady=6, padx=(0, 8))
        self.code_entry = ctk.CTkEntry(body, font=self.font, corner_radius=6, show='*',
                                       placeholder_text='邮箱授权码 / 客户端专用密码')
        self.code_entry.grid(row=5, column=1, sticky='ew', pady=6)
        self.code_btn_frame = ctk.CTkFrame(body, fg_color='transparent')
        self.code_btn_frame.grid(row=5, column=2, sticky='w', padx=(6, 0), pady=6)

        self.eye_btn = ctk.CTkButton(self.code_btn_frame, text='显示', width=48, height=28,
                                     corner_radius=6, font=('Microsoft YaHei', 11),
                                     fg_color='transparent', hover_color='#E5E7EB',
                                     text_color='#6B7280', command=self._toggle_show)
        self.eye_btn.pack(side='left', padx=(0, 4))
        self.help_btn = ctk.CTkButton(self.code_btn_frame, text='📖 教程', width=76, height=28,
                                      corner_radius=6, font=('Microsoft YaHei', 11),
                                      fg_color=accent, hover_color=accent_hover,
                                      text_color='#FFFFFF', command=self._open_help)
        self.help_btn.pack(side='left')

        # 自定义 SMTP 参数
        self.custom_frame = ctk.CTkFrame(body, fg_color='transparent')
        self.custom_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(self.custom_frame, text='SMTP 服务器:', font=self.font).grid(
            row=0, column=0, sticky='w', pady=4, padx=(0, 8))
        self.host_entry = ctk.CTkEntry(self.custom_frame, font=self.font, corner_radius=6,
                                       placeholder_text='smtp.example.com')
        self.host_entry.grid(row=0, column=1, sticky='ew', pady=4)

        ctk.CTkLabel(self.custom_frame, text='端口:', font=self.font).grid(
            row=1, column=0, sticky='w', pady=4, padx=(0, 8))
        self.port_entry = ctk.CTkEntry(self.custom_frame, font=self.font, corner_radius=6,
                                       placeholder_text='465')
        self.port_entry.grid(row=1, column=1, sticky='ew', pady=4)

        ctk.CTkLabel(self.custom_frame, text='使用 SSL:', font=self.font).grid(
            row=2, column=0, sticky='w', pady=4, padx=(0, 8))
        self.ssl_switch = ctk.CTkSwitch(self.custom_frame, text='', width=20)
        self.ssl_switch.grid(row=2, column=1, sticky='w', pady=4)
        self.ssl_switch.select()

        # 状态提示
        self.status_label = ctk.CTkLabel(
            body, text='', font=('Microsoft YaHei', 11), anchor='w',
            justify='left', wraplength=500, text_color='#6B7280')
        self.status_label.grid(row=8, column=0, columnspan=3, sticky='w', pady=(10, 6))

        # 底部按钮
        bottom = ctk.CTkFrame(body, fg_color='transparent')
        bottom.grid(row=9, column=0, columnspan=3, sticky='ew', pady=(6, 0))
        self.test_btn = ctk.CTkButton(bottom, text='测试并保存', height=40, corner_radius=8,
                                      font=('Microsoft YaHei', 13, 'bold'),
                                      fg_color=accent, hover_color=accent_hover,
                                      text_color='#FFFFFF', command=self._test_and_save)
        self.test_btn.pack(side='left', padx=(0, 8))
        self.save_btn = ctk.CTkButton(bottom, text='仅保存', height=40, width=96, corner_radius=8,
                                      font=('Microsoft YaHei', 12),
                                      fg_color='transparent', hover_color='#E5E7EB',
                                      text_color='#374151', command=self._save_only)
        self.save_btn.pack(side='left', padx=(0, 8))
        self.cancel_btn = ctk.CTkButton(bottom, text='取消', height=40, width=80, corner_radius=8,
                                        font=('Microsoft YaHei', 12),
                                        fg_color='transparent', hover_color='#E5E7EB',
                                        text_color='#6B7280', command=self.win.destroy)
        self.cancel_btn.pack(side='right')

        # 填充已有配置
        self._fill(self._settings)
        # 让弹窗出现在主窗口上方
        try:
            self.win.update_idletasks()
            x = self.master.winfo_rootx() + max(0, (self.master.winfo_width() - 560) // 2)
            y = self.master.winfo_rooty() + 60
            self.win.geometry(f'+{max(0, x)}+{max(0, y)}')
        except Exception:
            pass

    # ------------------------------------------------------------ 填充 / 联动
    def _fill(self, cfg):
        provider = cfg.get('provider') or mailer.DEFAULT_PROVIDER
        if provider not in mailer.provider_names():
            provider = mailer.DEFAULT_PROVIDER
        self.provider_entry.set(provider)

        self.account_entry.delete(0, tk.END)
        if cfg.get('account'):
            self.account_entry.insert(0, cfg['account'])
        self.code_entry.delete(0, tk.END)
        if cfg.get('auth_code'):
            self.code_entry.insert(0, cfg['auth_code'])

        info = mailer.provider_info(provider)
        self.host_entry.delete(0, tk.END)
        self.host_entry.insert(0, cfg.get('host') or info['host'])
        self.port_entry.delete(0, tk.END)
        self.port_entry.insert(0, str(cfg.get('port') or info['port']))
        if cfg.get('use_ssl') in (0, 1):
            self.ssl_switch.select() if int(cfg['use_ssl']) else self.ssl_switch.deselect()

        self._on_provider_changed(provider)

    def _on_provider_changed(self, provider):
        info = mailer.provider_info(provider)
        self.hint_label.configure(text=f'获取方式：{info["hint"]}')
        is_custom = (provider == '自定义SMTP')
        if is_custom:
            self.custom_frame.grid(row=7, column=0, columnspan=3, sticky='ew', pady=(4, 0))
        else:
            self.custom_frame.grid_forget()
            self.host_entry.delete(0, tk.END)
            self.host_entry.insert(0, info['host'])
            self.port_entry.delete(0, tk.END)
            self.port_entry.insert(0, str(info['port']))
            self.ssl_switch.select() if info['ssl'] else self.ssl_switch.deselect()
        self.help_btn.configure(state='normal' if info['help'] else 'disabled')

    def _open_help(self):
        info = mailer.provider_info(self.provider_entry.get())
        url = info.get('help')
        if url:
            webbrowser.open(url)
            self._set_status(f'已在浏览器打开 {self.provider_entry.get()} 的配置教程')
        else:
            self._set_status('该服务商没有内置教程，请向邮箱服务商确认 SMTP 参数', error=True)

    def _toggle_show(self):
        if self.code_entry.cget('show') == '*':
            self.code_entry.configure(show='')
            self.eye_btn.configure(text='隐藏')
        else:
            self.code_entry.configure(show='*')
            self.eye_btn.configure(text='显示')

    def _set_status(self, text, error=False):
        self.status_label.configure(text=text,
                                    text_color='#DC2626' if error else '#059669')

    # ------------------------------------------------------------ 收集 / 校验 / 保存
    def _collect(self):
        provider = self.provider_entry.get().strip() or mailer.DEFAULT_PROVIDER
        cfg = {
            'enabled': 1,
            'provider': provider,
            'account': self.account_entry.get().strip(),
            'auth_code': self.code_entry.get().strip(),
            'receiver': self.account_entry.get().strip(),
            'host': self.host_entry.get().strip(),
            'port': 0,
            'use_ssl': int(self.ssl_switch.get()),
        }
        try:
            cfg['port'] = int(self.port_entry.get().strip() or 0)
        except ValueError:
            cfg['port'] = 0
        return cfg

    def _validate(self, cfg):
        if not cfg['account'] or '@' not in cfg['account']:
            self._set_status('请填写正确的邮箱地址', error=True)
            return False
        if not cfg['auth_code']:
            self._set_status('请填写授权码（不是邮箱登录密码）', error=True)
            return False
        if cfg.get('receiver') and '@' not in cfg['receiver']:
            self._set_status('收件邮箱格式不正确', error=True)
            return False
        if cfg['provider'] == '自定义SMTP':
            if not cfg['host']:
                self._set_status('自定义 SMTP 需要填写服务器地址', error=True)
                return False
            if cfg['port'] <= 0:
                self._set_status('自定义 SMTP 需要填写有效端口', error=True)
                return False
        return True

    def _persist(self, cfg):
        if mailer.save_settings(cfg):
            self._settings = dict(cfg)
            if self.on_saved:
                try:
                    self.on_saved()
                except Exception:
                    pass
            return True
        self._set_status('保存失败，请检查 account_info.json 是否可写', error=True)
        return False

    def _test_and_save(self):
        cfg = self._collect()
        if not self._validate(cfg):
            return
        self._set_status('正在连接邮件服务器并发送测试邮件，请稍候…')
        self.test_btn.configure(state='disabled')
        try:
            self.win.update_idletasks()
            ok, message = mailer.test_connection(cfg)
        finally:
            self.test_btn.configure(state='normal')
        if not ok:
            self._set_status(f'测试失败：{message}', error=True)
            return
        if self._persist(cfg):
            self._set_status('测试成功，配置已保存，正在关闭…')
            self.result = True
            self.win.after(700, self.win.destroy)

    def _save_only(self):
        cfg = self._collect()
        if not self._validate(cfg):
            return
        if self._persist(cfg):
            self.result = True
            self.win.destroy()
