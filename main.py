import tkinter as tk
import json
import os
import threading
import keyboard
import time
import ctypes
import winshell
import sys
import shutil
import subprocess
from win32com.client import Dispatch

APP_NAME = "QuickToDo"
DATA_FILE = "todos.json"
SETTINGS_FILE = "settings.json"

GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x80000
WS_EX_TRANSPARENT = 0x20

LANGUAGES = {
    "de": {
        "title": "📝 QuickTodo",
        "settings": "⚙️ Einstellungen",
        "close": "✖ Schließen",
        "add": "+",
        "delete": "🗑",
        "hotkeys": "Hotkeys: ALT+Q (Öffnen/Schließen), \n ALT+T (Transparenz), ALT+C (Klickbar machen)",
        "settings_title": "Einstellungen",
        "spawn_direction": "Einblende-Richtung:",
        "margin_label": "Rand-Abstand (px):",
        "transparency_label": "Transparenz (%):",
        "clickthrough": "Fenster klick-durchlässig",
        "autostart": "Autostart aktivieren",
        "language_label": "Sprache auswählen:",
        "corners": {
            "top_left": "Oben Links",
            "top_right": "Oben Rechts",
            "bottom_left": "Unten Links",
            "bottom_right": "Unten Rechts"
        }
    },
    "en": {
        "title": "📝 QuickTodo",
        "settings": "⚙️ Settings",
        "close": "✖ Close",
        "add": "+",
        "delete": "🗑",
        "hotkeys": "Hotkeys: ALT+Q (Toggle), \n ALT+T (Transparency), ALT+C (Force Clickable)",
        "settings_title": "Settings",
        "spawn_direction": "Spawn Direction:",
        "margin_label": "Margin (px):",
        "transparency_label": "Transparency (%):",
        "clickthrough": "Window click-through",
        "autostart": "Enable Autostart",
        "language_label": "Select Language:",
        "corners": {
            "top_left": "Top Left",
            "top_right": "Top Right",
            "bottom_left": "Bottom Left",
            "bottom_right": "Bottom Right"
        }
    }
}

def create_startmenu_shortcut():
    startmenu = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs')
    shortcut_path = os.path.join(startmenu, f"{APP_NAME}.lnk")
    target = os.path.join(os.getenv('LOCALAPPDATA'), APP_NAME, f"{APP_NAME}.exe")

    if not os.path.exists(shortcut_path):
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = target
        shortcut.WorkingDirectory = os.path.dirname(target)
        shortcut.IconLocation = target
        shortcut.save()

def first_time_install():
    install_dir = os.path.join(os.getenv('LOCALAPPDATA'), APP_NAME)
    if not os.path.exists(install_dir):
        os.makedirs(install_dir)
    target_exe = os.path.join(install_dir, f"{APP_NAME}.exe")
    if not os.path.exists(target_exe):
        shutil.copy2(sys.argv[0], target_exe)
        subprocess.Popen(target_exe, shell=True)
        sys.exit()
    create_startmenu_shortcut()
    os.chdir(install_dir)

class TodoApp:
    def __init__(self):
        self.language = "en"
        self.root = tk.Tk()
        self.install_dir = os.path.join(os.getenv('LOCALAPPDATA'), APP_NAME)
        self.data_path = os.path.join(self.install_dir, DATA_FILE)
        self.settings_path = os.path.join(self.install_dir, SETTINGS_FILE)
        self.load_settings()
        self.load_tasks()
        self.setup_ui()
        self.visible = False
        self.transparency_enabled = True
        self.apply_clickthrough()
        self.update_listbox()
        if self.settings.get("autostart", False):
            self.create_autostart()

    def setup_ui(self):
        self.root.title(LANGUAGES[self.language]["title"])
        self.window_width = 370
        self.window_height = 580
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.calculate_start_position()
        self.root.geometry(f"{self.window_width}x{self.window_height}+{self.start_x}+{self.start_y}")
        self.root.configure(bg="#222222")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)
        self.root.attributes("-alpha", 0.0)

        self.main_frame = tk.Frame(self.root, bg="#222222")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.title_bar = tk.Frame(self.main_frame, bg="#333333", height=30)
        self.title_bar.place(x=0, y=0, relwidth=1)

        self.title_label = tk.Label(self.title_bar, text=LANGUAGES[self.language]["title"], bg="#333333", fg="white", font=("Segoe UI", 12))
        self.title_label.pack(side=tk.LEFT, padx=10)

        self.settings_button = tk.Button(self.title_bar, text=LANGUAGES[self.language]["settings"], bg="#333333", fg="white", bd=0, font=("Segoe UI", 12), command=self.open_settings)
        self.settings_button.pack(side=tk.RIGHT, padx=(0,5))

        self.close_button = tk.Button(self.title_bar, text=LANGUAGES[self.language]["close"], bg="#333333", fg="white", bd=0, font=("Segoe UI", 12), command=self.root.quit)
        self.close_button.pack(side=tk.RIGHT, padx=(0,10))

        self.todo_frame = tk.Frame(self.main_frame, bg="#222222")
        self.todo_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(40,10))

        self.listbox = tk.Listbox(self.todo_frame, font=("Segoe UI", 13), bg="#222222", fg="#eeeeee", selectbackground="#444444", selectforeground="#ffffff", activestyle="none", bd=0, highlightthickness=0)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        self.listbox.bind("<Button-1>", self.single_click_toggle_task)

        bottom_frame = tk.Frame(self.main_frame, bg="#222222")
        bottom_frame.pack(pady=5)

        self.entry = tk.Entry(bottom_frame, font=("Segoe UI", 13), bg="#333333", fg="white", insertbackground="white", width=20, relief="flat")
        self.entry.grid(row=0, column=0, padx=5)
        self.entry.bind("<Return>", self.add_task)

        add_button = tk.Button(bottom_frame, text=LANGUAGES[self.language]["add"], font=("Segoe UI", 14), bg="#4CAF50", fg="white", width=3, bd=0, command=self.add_task)
        add_button.grid(row=0, column=1, padx=5)

        delete_button = tk.Button(bottom_frame, text=LANGUAGES[self.language]["delete"], font=("Segoe UI", 14), bg="#f44336", fg="white", width=3, bd=0, command=self.delete_task)
        delete_button.grid(row=0, column=2, padx=5)

        self.hotkey_label = tk.Label(self.main_frame, text=LANGUAGES[self.language]["hotkeys"], font=("Segoe UI", 9), bg="#222222", fg="#777777")
        self.hotkey_label.pack(pady=(0,10))

    def calculate_start_position(self):
        corner = self.settings.get("spawn_corner", "top_left")
        margin = int(self.settings.get("margin", 20))
        if corner == "top_left":
            self.start_x = margin
            self.start_y = margin
        elif corner == "top_right":
            self.start_x = self.screen_width - self.window_width - margin
            self.start_y = margin
        elif corner == "bottom_left":
            self.start_x = margin
            self.start_y = self.screen_height - self.window_height - margin
        elif corner == "bottom_right":
            self.start_x = self.screen_width - self.window_width - margin
            self.start_y = self.screen_height - self.window_height - margin

    def apply_clickthrough(self):
        hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        if self.settings.get("clickthrough", False):
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_LAYERED | WS_EX_TRANSPARENT)
        else:
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style & ~WS_EX_TRANSPARENT)

    def load_settings(self):
        if os.path.exists(self.settings_path):
            with open(self.settings_path, "r", encoding="utf-8") as f:
                self.settings = json.load(f)
        else:
            self.settings = {
                "spawn_corner": "top_left",
                "margin": 20,
                "transparency": 1.0,
                "clickthrough": False,
                "autostart": False
            }
            self.save_settings()

    def save_settings(self):
        with open(self.settings_path, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, indent=2)

    def load_tasks(self):
        if os.path.exists(self.data_path):
            with open(self.data_path, "r", encoding="utf-8") as f:
                self.tasks = json.load(f)
        else:
            self.tasks = []

    def save_tasks(self):
        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump(self.tasks, f, indent=2)

    def animate_show(self):
        self.root.deiconify()
        for i in range(0, 11):
            self.root.attributes("-alpha", i * 0.1)
            self.root.update()
            time.sleep(0.02)

    def animate_hide(self):
        for i in reversed(range(0, 11)):
            self.root.attributes("-alpha", i * 0.1)
            self.root.update()
            time.sleep(0.02)
        self.root.withdraw()

    def toggle_window(self):
        if self.visible:
            self.animate_hide()
        else:
            self.animate_show()
        self.visible = not self.visible

    def toggle_transparency(self):
        if self.transparency_enabled:
            self.root.attributes("-alpha", 1.0)
            self.transparency_enabled = False
        else:
            self.root.attributes("-alpha", self.settings.get("transparency", 1.0))
            self.transparency_enabled = True

    def force_disable_clickthrough(self):
        self.settings["clickthrough"] = False
        self.save_settings()
        self.apply_clickthrough()

    def add_task(self, event=None):
        task = self.entry.get().strip()
        if task:
            self.tasks.append({"task": task, "done": False})
            self.entry.delete(0, tk.END)
            self.update_listbox()
            self.save_tasks()

    def delete_task(self):
        selected = self.listbox.curselection()
        if selected:
            del self.tasks[selected[0]]
            self.update_listbox()
            self.save_tasks()

    def toggle_task_done(self, index):
        if 0 <= index < len(self.tasks):
            self.tasks[index]["done"] = not self.tasks[index]["done"]
            self.update_listbox()
            self.save_tasks()

    def single_click_toggle_task(self, event):
        index = self.listbox.nearest(event.y)
        self.toggle_task_done(index)

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for task in self.tasks:
            prefix = "✅" if task["done"] else "🔲"
            self.listbox.insert(tk.END, f"{prefix} {task['task']}")

    def create_autostart(self):
        startup = winshell.startup()
        shortcut_path = os.path.join(startup, f"{APP_NAME}.lnk")
        if not os.path.exists(shortcut_path):
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = os.path.abspath(sys.argv[0])
            shortcut.WorkingDirectory = os.path.dirname(os.path.abspath(sys.argv[0]))
            shortcut.IconLocation = os.path.abspath(sys.argv[0])
            shortcut.save()

    def remove_autostart(self):
        startup = winshell.startup()
        shortcut_path = os.path.join(startup, f"{APP_NAME}.lnk")
        if os.path.exists(shortcut_path):
            os.remove(shortcut_path)

    def refresh_language(self):
        self.title_label.config(text=LANGUAGES[self.language]["title"])
        self.settings_button.config(text=LANGUAGES[self.language]["settings"])
        self.close_button.config(text=LANGUAGES[self.language]["close"])
        self.hotkey_label.config(text=LANGUAGES[self.language]["hotkeys"])

    def open_settings(self):
        settings_win = tk.Toplevel(self.root)
        settings_win.title(LANGUAGES[self.language]["settings_title"])
        settings_win.geometry("320x650")
        settings_win.configure(bg="#333333")
        settings_win.attributes("-topmost", True)

        def save_and_refresh():
            self.save_settings()
            self.calculate_start_position()
            self.root.geometry(f"{self.window_width}x{self.window_height}+{self.start_x}+{self.start_y}")
            self.root.attributes("-alpha", self.settings.get("transparency", 1.0))

        def update_margin(event=None):
            try:
                self.settings["margin"] = int(margin_entry.get())
                save_and_refresh()
            except ValueError:
                pass

        def update_transparency(event=None):
            try:
                self.settings["transparency"] = max(0.1, min(int(transparency_entry.get()) / 100, 1.0))
                save_and_refresh()
            except ValueError:
                pass

        def update_clickthrough():
            self.settings["clickthrough"] = bool(clickthrough_var.get())
            self.save_settings()
            self.apply_clickthrough()

        def update_autostart():
            self.settings["autostart"] = bool(autostart_var.get())
            self.save_settings()
            if self.settings["autostart"]:
                self.create_autostart()
            else:
                self.remove_autostart()

        def change_language(lang):
            self.language = lang
            self.refresh_language()
            settings_win.destroy()

        tk.Label(settings_win, text=LANGUAGES[self.language]["spawn_direction"], bg="#333333", fg="white", font=("Segoe UI", 12)).pack(pady=10)
        for key, label in LANGUAGES[self.language]["corners"].items():
            tk.Button(settings_win, text=label, command=lambda c=key: (self.settings.update({"spawn_corner": c}), save_and_refresh()), font=("Segoe UI", 11), bg="#555555", fg="white", bd=0).pack(fill=tk.X, padx=20, pady=5)

        tk.Label(settings_win, text=LANGUAGES[self.language]["margin_label"], bg="#333333", fg="white", font=("Segoe UI", 12)).pack(pady=(20, 5))
        margin_entry = tk.Entry(settings_win, font=("Segoe UI", 12), bg="#555555", fg="white", bd=0, justify="center")
        margin_entry.insert(0, str(self.settings.get("margin", 20)))
        margin_entry.pack(padx=50)
        margin_entry.bind("<FocusOut>", update_margin)
        margin_entry.bind("<Return>", update_margin)

        tk.Label(settings_win, text=LANGUAGES[self.language]["transparency_label"], bg="#333333", fg="white", font=("Segoe UI", 12)).pack(pady=(20, 5))
        transparency_entry = tk.Entry(settings_win, font=("Segoe UI", 12), bg="#555555", fg="white", bd=0, justify="center")
        transparency_entry.insert(0, str(int(self.settings.get("transparency", 1.0) * 100)))
        transparency_entry.pack(padx=50)
        transparency_entry.bind("<FocusOut>", update_transparency)
        transparency_entry.bind("<Return>", update_transparency)

        clickthrough_var = tk.IntVar(value=int(self.settings.get("clickthrough", False)))
        tk.Checkbutton(settings_win, text=LANGUAGES[self.language]["clickthrough"], variable=clickthrough_var, command=update_clickthrough, bg="#333333", fg="white", activebackground="#333333", activeforeground="white", selectcolor="#333333").pack(pady=10)

        autostart_var = tk.IntVar(value=int(self.settings.get("autostart", False)))
        tk.Checkbutton(settings_win, text=LANGUAGES[self.language]["autostart"], variable=autostart_var, command=update_autostart, bg="#333333", fg="white", activebackground="#333333", activeforeground="white", selectcolor="#333333").pack(pady=10)

        tk.Label(settings_win, text=LANGUAGES[self.language]["language_label"], bg="#333333", fg="white", font=("Segoe UI", 12)).pack(pady=(20, 5))
        lang_var = tk.StringVar(value=self.language)
        lang_dropdown = tk.OptionMenu(settings_win, lang_var, *LANGUAGES.keys(), command=change_language)
        lang_dropdown.config(bg="#555555", fg="white", activebackground="#777777", font=("Segoe UI", 11))
        lang_dropdown["menu"].config(bg="#555555", fg="white", activebackground="#777777")
        lang_dropdown.pack(padx=50)

def run_hotkeys(app):
    keyboard.add_hotkey("alt+q", app.toggle_window)
    keyboard.add_hotkey("alt+t", app.toggle_transparency)
    keyboard.add_hotkey("alt+c", app.force_disable_clickthrough)
    keyboard.wait()

if __name__ == "__main__":
    first_time_install()
    app = TodoApp()
    threading.Thread(target=run_hotkeys, args=(app,), daemon=True).start()
    app.animate_show()
    app.root.mainloop()
