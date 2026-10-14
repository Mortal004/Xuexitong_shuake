""""悬停提示组件"""
import tkinter as tk

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind('<Enter>', self.show_tip)
        self.widget.bind('<Leave>', self.hide_tip)

    def show_tip(self, event=None):
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
        self.text = new_text