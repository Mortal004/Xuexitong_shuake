"""赞助页面 — 打赏二维码、邮箱复制等 UI 和交互逻辑"""
import tkinter as tk
from tkinter import messagebox
from PIL import Image
import customtkinter as ctk

class SponsorPanel:
    def __init__(self, parent, get_font, get_colors, root):
        self.parent = parent
        self._get_font = get_font
        self._get_colors = get_colors
        self.root = root
        self._build_ui()

    @property
    def _font(self):
        return self._get_font()

    @property
    def _colors(self):
        return self._get_colors()

    def _build_ui(self):
        colors = self._colors

        self.title = ctk.CTkLabel(self.parent, text="❤️ 赞助作者",
                                  font=ctk.CTkFont(size=20, weight="bold"),
                                  fg_color='transparent')
        self.title.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 8), sticky=tk.W)

        self.desc = ctk.CTkLabel(self.parent,
                                 text="如果本软件对您有帮助，欢迎打赏支持！\n您的支持是我持续更新的最大动力 😊",
                                 font=self._font, fg_color='transparent', justify="left")
        self.desc.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 10), sticky=tk.W)

        self.separator = ctk.CTkFrame(self.parent, height=2, fg_color=colors[0])
        self.separator.grid(row=2, column=0, columnspan=2, padx=20, pady=8, sticky="ew")

        self.qr_label = ctk.CTkLabel(self.parent, text="📱 微信扫码打赏",
                                     font=ctk.CTkFont(size=14, weight="bold"),
                                     fg_color='transparent')
        self.qr_label.grid(row=3, column=0, columnspan=2, padx=20, pady=(10, 5))

        self.money_image = Image.open(r"task/img/money.png")
        self.money_photo = ctk.CTkImage(self.money_image, size=(280, 320))
        self.qr_image = ctk.CTkLabel(self.parent, text='', image=self.money_photo, fg_color='transparent')
        self.qr_image.grid(row=4, column=0, columnspan=2, padx=20, pady=(0, 10))

        self.email_frame = ctk.CTkFrame(self.parent, fg_color='transparent')
        self.email_frame.grid(row=5, column=0, columnspan=2, padx=20, pady=(10, 5), sticky="ew")
        self.email_label = ctk.CTkLabel(self.email_frame, text="📧 联系邮箱：",
                                        font=ctk.CTkFont(size=13, weight="bold"),
                                        fg_color='transparent')
        self.email_label.pack(side="left")
        self.email_value = ctk.CTkLabel(self.email_frame, text="2022865286@qq.com",
                                        font=self._font, fg_color='transparent',
                                        text_color=colors[0])
        self.email_value.pack(side="left", padx=(5, 10))

        self.copy_btn = ctk.CTkButton(self.email_frame, text="📋 复制", width=70, height=28,
                                      fg_color=colors[0], hover_color=colors[2],
                                      font=ctk.CTkFont(size=11),
                                      command=self._copy_email)
        self.copy_btn.pack(side="left")

        self.tip = ctk.CTkLabel(self.parent,
                                text="⚠️ 打赏后请发送邮件告知作者，以便获取API密钥",
                                font=ctk.CTkFont(size=11), fg_color='transparent', text_color="gray")
        self.tip.grid(row=6, column=0, columnspan=2, padx=20, pady=(5, 20), sticky=tk.W)

    def _copy_email(self):
        """复制赞助邮箱到剪贴板"""
        self.root.clipboard_clear()
        self.root.clipboard_append("2022865286@qq.com")
        messagebox.showinfo("已复制", "邮箱地址已复制到剪贴板！")

    def update_theme(self, colors):
        """随主题切换更新颜色"""
        self.separator.configure(fg_color=colors[0])
        self.email_value.configure(text_color=colors[0])
        self.copy_btn.configure(fg_color=colors[0], hover_color=colors[2])
