import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import customtkinter as ctk
import subprocess
import time
import os
import json
import random
import threading
import sys
import urllib.request
import webbrowser
import queue
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from datetime import datetime

__version__ = "5"
UPDATE_URL = "https://raw.githubusercontent.com/versozadarwin23/autopost/refs/heads/main/main.py"
VERSION_CHECK_URL = "https://raw.githubusercontent.com/versozadarwin23/autopost/refs/heads/main/version.txt"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

COLORS = {
    "bg_main": "#0D1117",
    "bg_card": "#161B22",
    "bg_lighter": "#21262D",
    "primary": "#58A6FF",
    "success": "#2EA043",
    "warning": "#E3B341",
    "danger": "#F85149",
    "text_main": "#C9D1D9",
    "text_sub": "#8B949E",
    "border": "#30363D"
}

FONT_HEADER = ("Roboto", 18, "bold")
FONT_SUBHEADER = ("Roboto", 13, "bold")
FONT_BODY = ("Roboto", 11)


class StatCard(ctk.CTkFrame):
    def __init__(self, parent, title, value, icon, color):
        super().__init__(parent, fg_color=COLORS["bg_card"], corner_radius=10, border_width=1,
                         border_color=COLORS["border"])
        self.value_var = ctk.StringVar(value=str(value))
        self.icon_label = ctk.CTkLabel(self, text=icon, font=("Segoe UI Emoji", 20))
        self.icon_label.place(relx=0.85, rely=0.25, anchor="center")
        self.title_label = ctk.CTkLabel(self, text=title.upper(), font=("Roboto", 10, "bold"),
                                        text_color=COLORS["text_sub"])
        self.title_label.pack(anchor="w", padx=10, pady=(8, 0))
        self.value_label = ctk.CTkLabel(self, textvariable=self.value_var, font=("Roboto", 22, "bold"),
                                        text_color=color)
        self.value_label.pack(anchor="w", padx=10, pady=(0, 8))

    def update_value(self, new_value):
        self.value_var.set(str(new_value))


class StatsFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        title = ctk.CTkLabel(self, text="📊 LIVE ANALYTICS", font=FONT_SUBHEADER, text_color=COLORS["primary"])
        title.pack(anchor="w", pady=(0, 5))
        self.grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True)
        self.grid_frame.grid_columnconfigure((0, 1), weight=1)
        self.card_shares = StatCard(self.grid_frame, "Total Shares", "0", "🚀", COLORS["success"])
        self.card_shares.grid(row=0, column=0, padx=(0, 3), pady=3, sticky="ew")
        self.card_failed = StatCard(self.grid_frame, "Failed", "0", "⚠️", COLORS["danger"])
        self.card_failed.grid(row=0, column=1, padx=(3, 0), pady=3, sticky="ew")
        self.card_devices = StatCard(self.grid_frame, "Active Devices", "0", "📱", COLORS["warning"])
        self.card_devices.grid(row=1, column=0, columnspan=2, padx=0, pady=(3, 3), sticky="ew")

    def update_stats(self, shares, failed):
        self.card_shares.update_value(shares)
        self.card_failed.update_value(failed)

    def update_devices(self, count):
        self.card_devices.update_value(count)


class DeviceFrame(ctk.CTkFrame):
    def __init__(self, parent, device_id):
        super().__init__(parent, fg_color=COLORS["bg_card"], corner_radius=8, border_width=1,
                         border_color=COLORS["border"])
        self.device_id = device_id
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=8)
        self.device_label = ctk.CTkLabel(header_frame, text=f"📱 {device_id}", font=("Roboto", 12, "bold"),
                                         text_color=COLORS["primary"])
        self.device_label.pack(side="left")
        self.info_label = ctk.CTkLabel(header_frame, text="Syncing...", font=("Roboto", 10),
                                       text_color=COLORS["text_sub"])
        self.info_label.pack(side="right")

    def update_device_info(self, model, version):
        info_text = f"{model} • A{version}"
        try:
            if self.info_label.winfo_exists():
                self.info_label.configure(text=info_text)
        except:
            pass


class PairFrame(ctk.CTkFrame):
    def __init__(self, parent, pair_num, on_remove):
        super().__init__(parent, fg_color=COLORS["bg_lighter"], corner_radius=8, border_width=1,
                         border_color=COLORS["border"])
        self.on_remove = on_remove
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(8, 2))
        self.header_label = ctk.CTkLabel(header, text=f"📍 LINK #{pair_num}", font=("Roboto", 12, "bold"),
                                         text_color=COLORS["primary"])
        self.header_label.pack(side="left")
        if pair_num > 1:
            btn_del = ctk.CTkButton(header, text="✖", width=25, height=25, fg_color="transparent",
                                    hover_color=COLORS["danger"], text_color=COLORS["text_sub"], corner_radius=6,
                                    command=self.remove)
            btn_del.pack(side="right")
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="x", padx=10, pady=(0, 10))
        self.link_entry = ctk.CTkEntry(content, height=30, placeholder_text="Enter Target URL",
                                       fg_color=COLORS["bg_main"], border_color=COLORS["border"], corner_radius=6,
                                       font=FONT_BODY)
        self.link_entry.pack(fill="x", pady=(0, 8))
        cap_row = ctk.CTkFrame(content, fg_color="transparent")
        cap_row.pack(fill="x")
        self.caption_path = ctk.CTkEntry(cap_row, height=30, placeholder_text="Caption File (.txt)",
                                         fg_color=COLORS["bg_main"], border_color=COLORS["border"], corner_radius=6,
                                         font=FONT_BODY)
        self.caption_path.pack(side="left", fill="x", expand=True, padx=(0, 5))
        btn_browse = ctk.CTkButton(cap_row, text="📂", width=40, height=30, fg_color=COLORS["bg_card"],
                                   hover_color=COLORS["primary"], border_width=1, border_color=COLORS["border"],
                                   corner_radius=6, command=self.browse_caption)
        btn_browse.pack(side="right")

    def remove(self):
        self.on_remove()

    def browse_caption(self):
        file = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file:
            self.caption_path.delete(0, "end")
            self.caption_path.insert(0, file)


class FacebookAutomationGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.start_time = None
        self.log_storage = {"auto": [], "debug": [], "sys": []}
        self.current_log_device = "GLOBAL"
        self.saved_settings = {}
        self.active_drivers = []
        self.cookie_queue = queue.Queue()

        self.title(f"AutoPost V{__version__}")
        self.geometry("1100x700")
        self.after(0, lambda: self.state("zoomed"))
        self.configure(fg_color=COLORS["bg_main"])

        self.is_running = False
        self.chrome_driver_path = "chromedriver.exe"
        self.global_cookie_path = ""
        self.devices = []
        self.active_devices_set = set()
        self.device_resolutions = {}
        self.device_widgets = []
        self.pair_widgets = []
        self.total_shares = 0
        self.error_count = 0
        self.total_attempts = 0
        self.job_list_global = []

        threading.Thread(target=self.device_monitor_thread, daemon=True).start()

        self.load_settings()
        self.layout_ui()
        self.refresh_devices()
        self.check_for_updates()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def check_for_updates(self, manual=False):
        if manual:
            self.status_badge.configure(text="● CHECKING...", text_color=COLORS["warning"])

        def _check():
            try:
                req = urllib.request.Request(VERSION_CHECK_URL, headers={'Cache-Control': 'no-cache'})
                with urllib.request.urlopen(req, timeout=5) as response:
                    remote_version = response.read().decode('utf-8').strip()
                if remote_version and remote_version != __version__:
                    self.after(0, lambda: self.show_update_popup(remote_version))
                else:
                    if manual:
                        self.after(0, lambda: messagebox.showinfo("Up to Date", f"Latest Version: V{__version__}"))
            except:
                pass
            finally:
                if manual:
                    self.after(0, lambda: self.status_badge.configure(text="● IDLE", text_color=COLORS["text_sub"]))

        threading.Thread(target=_check, daemon=True).start()

    def show_update_popup(self, remote_version):
        if messagebox.askyesno("Update Available", f"New Version V{remote_version} available. Update now?"):
            self.perform_update()

    def perform_update(self):
        self.status_badge.configure(text="● UPDATING...", text_color=COLORS["warning"])

        def _download_and_replace():
            try:
                req = urllib.request.Request(UPDATE_URL, headers={'Cache-Control': 'no-cache'})
                with urllib.request.urlopen(req, timeout=10) as response:
                    new_code = response.read()
                with open("main_update.py", "wb") as f:
                    f.write(new_code)
                script_name = os.path.basename(sys.argv[0])
                if not script_name.endswith('.py'):
                    script_name = "main.py"
                bat_code = f"""@echo off\ntimeout /t 2\nmove /y main_update.py "{script_name}"\nstart python "{script_name}"\ndel "%~f0"\n"""
                with open("updater.bat", "w") as f:
                    f.write(bat_code)
                subprocess.Popen("updater.bat", creationflags=subprocess.CREATE_NEW_CONSOLE)
                self.after(0, self.on_close)
            except:
                pass

        threading.Thread(target=_download_and_replace, daemon=True).start()

    def device_monitor_thread(self):
        while True:
            try:
                CREATE_NO_WINDOW = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                o = subprocess.check_output(["adb", "devices"], creationflags=CREATE_NO_WINDOW).decode("utf-8")
                current_devices = [l.split()[0] for l in o.strip().split("\n")[1:] if
                                   "device" in l and not l.startswith("*")]
                if set(current_devices) != set(getattr(self, 'devices', [])):
                    self.devices = current_devices
                    self.after(0, self.refresh_devices)
                    if self.is_running:
                        self.after(0, lambda: self.overall_stats.update_devices(len(self.active_devices_set)))
                        for dev in current_devices:
                            if dev not in self.active_devices_set and not self.single_dev_var.get():
                                self.active_devices_set.add(dev)
                                t = threading.Thread(target=self.run_fb_automation, args=(dev,))
                                t.start()
            except:
                pass
            time.sleep(3)

    def layout_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], height=50, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")

        ctk.CTkLabel(header, text=f"AUTOPOST V{__version__}", font=FONT_HEADER, text_color=COLORS["primary"]).pack(
            side="left", padx=15, pady=10)
        self.status_badge = ctk.CTkLabel(header, text="● IDLE", font=("Roboto", 12, "bold"),
                                         text_color=COLORS["text_sub"])
        self.status_badge.pack(side="right", padx=15)

        main_content = ctk.CTkFrame(self, fg_color="transparent")
        main_content.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        main_content.grid_rowconfigure(0, weight=1)
        main_content.grid_columnconfigure(0, weight=1)

        self.tabview = ctk.CTkTabview(main_content, fg_color=COLORS["bg_main"], corner_radius=10)
        self.tabview.grid(row=0, column=0, sticky="nsew")

        self.tab_dash = self.tabview.add(" Dashboard ")
        self.tab_devices = self.tabview.add(" Devices ")
        self.tab_config = self.tabview.add(" Settings ")
        self.tab_logs = self.tabview.add(" System Logs ")
        self.tab_adb = self.tabview.add(" ADB Tools ")

        self.setup_dashboard()
        self.setup_devices()
        self.setup_config()
        self.setup_logs()
        self.setup_adb()

    def setup_dashboard(self):
        self.tab_dash.grid_columnconfigure(1, weight=1)
        self.tab_dash.grid_rowconfigure(0, weight=1)

        # Scrollable Left Panel to fit everything on small screens
        left_panel = ctk.CTkScrollableFrame(self.tab_dash, fg_color="transparent", width=330)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        self.overall_stats = StatsFrame(left_panel)
        self.overall_stats.pack(fill="x", pady=(0, 10))

        # --- ACTIONS / CONTROLS FRAME ---
        control_frame = ctk.CTkFrame(left_panel, fg_color=COLORS["bg_card"], corner_radius=10)
        control_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(control_frame, text="AUTOMATION CONTROL", font=("Roboto", 11, "bold"),
                     text_color=COLORS["text_sub"]).pack(anchor="w", padx=15, pady=(10, 5))

        # Run Mode: All vs Single
        run_mode_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        run_mode_frame.pack(fill="x", padx=10, pady=5)

        self.single_dev_var = ctk.BooleanVar(value=False)
        self.single_dev_switch = ctk.CTkSwitch(run_mode_frame, text="Single Device Only", variable=self.single_dev_var,
                                               font=FONT_BODY, command=self.toggle_run_ui)
        self.single_dev_switch.pack(side="left")

        # Device Selector (Hidden by default unless Single is Checked)
        self.dash_device_select = ctk.CTkOptionMenu(run_mode_frame, width=120, height=25, font=FONT_BODY,
                                                    values=["Select Device"])
        self.dash_device_select.pack(side="right", padx=5)
        self.dash_device_select.configure(state="disabled")

        # Stagger Switch
        stagger_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        stagger_frame.pack(fill="x", padx=10, pady=5)
        self.stagger_var = ctk.BooleanVar(value=True)
        self.stagger_switch = ctk.CTkSwitch(stagger_frame, text="Slow Start (Stagger)", variable=self.stagger_var,
                                            font=FONT_BODY, progress_color=COLORS["warning"])
        self.stagger_switch.pack(side="left")
        self.stagger_delay_entry = ctk.CTkEntry(stagger_frame, width=40, height=25, justify="center", font=FONT_BODY)
        self.stagger_delay_entry.insert(0, "8")
        self.stagger_delay_entry.pack(side="right")
        ctk.CTkLabel(stagger_frame, text="Secs:", font=("Roboto", 10)).pack(side="right", padx=5)

        # Start/Stop
        btn_grid = ctk.CTkFrame(control_frame, fg_color="transparent")
        btn_grid.pack(fill="x", padx=10, pady=5)
        self.start_btn = ctk.CTkButton(btn_grid, text="▶ START", height=40, fg_color=COLORS["success"],
                                       hover_color="#1E8233", font=("Roboto", 13, "bold"), command=self.start_threads)
        self.start_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.stop_btn = ctk.CTkButton(btn_grid, text="⏹ STOP", height=40, fg_color=COLORS["danger"],
                                      hover_color="#C53030", font=("Roboto", 13, "bold"), state="disabled",
                                      command=self.stop_automation)
        self.stop_btn.pack(side="left", fill="x", expand=True, padx=(5, 0))

        # Delays
        lbl_delay = ctk.CTkLabel(control_frame, text="Pre/Post Action Delay (s)", font=("Roboto", 11, "bold"),
                                 text_color=COLORS["text_sub"])
        lbl_delay.pack(anchor="w", padx=15, pady=(5, 0))
        delay_row = ctk.CTkFrame(control_frame, fg_color="transparent")
        delay_row.pack(fill="x", padx=10, pady=(0, 10))
        self.dash_pre_delay = ctk.CTkEntry(delay_row, width=60, height=28, justify="center")
        self.dash_pre_delay.pack(side="left", padx=5)
        self.dash_pre_delay.insert(0, "10")
        ctk.CTkLabel(delay_row, text="/", font=("Roboto", 14, "bold")).pack(side="left")
        self.dash_post_delay = ctk.CTkEntry(delay_row, width=60, height=28, justify="center")
        self.dash_post_delay.pack(side="left", padx=5)
        self.dash_post_delay.insert(0, "10")

        # --- DEVICE ACTIONS ---
        ctk.CTkLabel(control_frame, text="DEVICE ACTIONS", font=("Roboto", 11, "bold"),
                     text_color=COLORS["primary"]).pack(anchor="w", padx=15, pady=(5, 2))

        # Row 1: Unlock, Home, Awake
        row_act1 = ctk.CTkFrame(control_frame, fg_color="transparent")
        row_act1.pack(fill="x", padx=10, pady=2)
        ctk.CTkButton(row_act1, text="🔓 Unlock", width=80, height=30, fg_color=COLORS["primary"], font=FONT_BODY,
                      command=self.action_go_home).pack(side="left", fill="x", expand=True, padx=2)
        ctk.CTkButton(row_act1, text="🏠 Home", width=80, height=30, fg_color=COLORS["primary"], font=FONT_BODY,
                      command=self.action_home_only).pack(side="left", fill="x", expand=True, padx=2)
        ctk.CTkButton(row_act1, text="💡 Awake", width=80, height=30, fg_color="#8957e5", hover_color="#6e44b8",
                      font=FONT_BODY, command=self.action_stay_awake).pack(side="left", fill="x", expand=True, padx=2)

        # --- SYSTEM ACTIONS ---
        ctk.CTkLabel(control_frame, text="SYSTEM ACTIONS", font=("Roboto", 11, "bold"),
                     text_color=COLORS["danger"]).pack(anchor="w", padx=15, pady=(10, 2))

        # Row 2: Reset, Reboot
        row_act2 = ctk.CTkFrame(control_frame, fg_color="transparent")
        row_act2.pack(fill="x", padx=10, pady=2)
        ctk.CTkButton(row_act2, text="⚡ Force Reset", height=30, fg_color=COLORS["warning"], text_color="#000",
                      hover_color="#B79034", font=FONT_BODY, command=self.system_full_reset).pack(side="left", fill="x",
                                                                                                  expand=True, padx=2)
        ctk.CTkButton(row_act2, text="🔄 Reboot All", height=30, fg_color=COLORS["danger"], hover_color="#C53030",
                      font=FONT_BODY, command=self.reboot_all_devices).pack(side="left", fill="x", expand=True, padx=2)

        # Check Update
        ctk.CTkButton(control_frame, text="☁ Check Updates", height=30, fg_color="#238636", hover_color="#2EA043",
                      font=FONT_BODY, command=lambda: self.check_for_updates(True)).pack(fill="x", padx=12,
                                                                                         pady=(5, 15))

        # Right Panel (Links)
        right_panel = ctk.CTkFrame(self.tab_dash, fg_color=COLORS["bg_card"], corner_radius=10)
        right_panel.grid(row=0, column=1, sticky="nsew")
        header = ctk.CTkFrame(right_panel, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=15)
        ctk.CTkLabel(header, text="TASKS", font=FONT_SUBHEADER, text_color=COLORS["primary"]).pack(side="left")
        ctk.CTkButton(header, text="+ Add", width=80, height=30, fg_color=COLORS["primary"], font=FONT_BODY,
                      command=self.add_pair).pack(side="right")
        self.pairs_scroll = ctk.CTkScrollableFrame(right_panel, fg_color="transparent")
        self.pairs_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        self.add_pair()

    def toggle_run_ui(self):
        if self.single_dev_var.get():
            self.dash_device_select.configure(state="normal")
        else:
            self.dash_device_select.configure(state="disabled")

    def setup_devices(self):
        self.tab_devices.grid_columnconfigure(0, weight=1)
        self.tab_devices.grid_rowconfigure(1, weight=1)
        toolbar = ctk.CTkFrame(self.tab_devices, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.device_count_label = ctk.CTkLabel(toolbar, text="Connected: 0", font=FONT_SUBHEADER)
        self.device_count_label.pack(side="left", padx=10)
        ctk.CTkButton(toolbar, text="🔄 Refresh", width=100, height=30, fg_color=COLORS["bg_card"], border_width=1,
                      border_color=COLORS["border"], command=self.refresh_devices).pack(side="right", padx=10)
        self.device_config_frame = ctk.CTkScrollableFrame(self.tab_devices, fg_color=COLORS["bg_lighter"],
                                                          corner_radius=10)
        self.device_config_frame.grid(row=1, column=0, sticky="nsew")

    def setup_config(self):
        container = ctk.CTkFrame(self.tab_config, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=10, pady=10)

        f1 = ctk.CTkFrame(container, fg_color=COLORS["bg_card"], corner_radius=10)
        f1.pack(fill="x", pady=5)
        ctk.CTkLabel(f1, text="PATHS", font=FONT_SUBHEADER, text_color=COLORS["primary"]).pack(anchor="w", padx=15,
                                                                                               pady=10)

        r1 = ctk.CTkFrame(f1, fg_color="transparent")
        r1.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(r1, text="Chromedriver:", width=100, anchor="w").pack(side="left")
        self.driver_entry = ctk.CTkEntry(r1)
        self.driver_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.driver_entry.insert(0, self.chrome_driver_path)
        ctk.CTkButton(r1, text="📂", width=40, command=self.browse_driver).pack(side="right")

        r2 = ctk.CTkFrame(f1, fg_color="transparent")
        r2.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(r2, text="Cookies.txt:", width=100, anchor="w").pack(side="left")
        self.cookie_entry = ctk.CTkEntry(r2)
        self.cookie_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.cookie_entry.insert(0, self.global_cookie_path)
        ctk.CTkButton(r2, text="📂", width=40, command=self.browse_global_cookie).pack(side="right")

        f2 = ctk.CTkFrame(container, fg_color=COLORS["bg_card"], corner_radius=10)
        f2.pack(fill="x", pady=10)
        ctk.CTkLabel(f2, text="LIMITS & DELAYS", font=FONT_SUBHEADER, text_color=COLORS["primary"]).pack(anchor="w",
                                                                                                         padx=15,
                                                                                                         pady=10)

        r3 = ctk.CTkFrame(f2, fg_color="transparent")
        r3.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(r3, text="Random Delay (s):").pack(side="left")
        self.min_delay = ctk.CTkEntry(r3, width=50, justify="center")
        self.min_delay.pack(side="left", padx=5)
        self.min_delay.insert(0, "5")
        ctk.CTkLabel(r3, text="-").pack(side="left")
        self.max_delay = ctk.CTkEntry(r3, width=50, justify="center")
        self.max_delay.pack(side="left", padx=5)
        self.max_delay.insert(0, "10")

        r4 = ctk.CTkFrame(f2, fg_color="transparent")
        r4.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(r4, text="Max Cookies/Device (0=Unl):").pack(side="left")
        self.cookie_limit_entry = ctk.CTkEntry(r4, width=60, justify="center")
        self.cookie_limit_entry.pack(side="left", padx=10)
        self.cookie_limit_entry.insert(0, "0")

        r5 = ctk.CTkFrame(f2, fg_color="transparent")
        r5.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(r5, text="Max Retries:").pack(side="left")
        self.retry_count = ctk.CTkEntry(r5, width=60, justify="center")
        self.retry_count.pack(side="left", padx=10)
        self.retry_count.insert(0, "3")

        ctk.CTkButton(container, text="💾 SAVE CONFIG", height=40, fg_color=COLORS["primary"],
                      command=self.save_config).pack(pady=10)

    def setup_logs(self):
        self.tab_logs.grid_columnconfigure(0, weight=1)
        self.tab_logs.grid_rowconfigure(1, weight=1)

        top_bar = ctk.CTkFrame(self.tab_logs, fg_color="transparent", height=40)
        top_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=(5, 5))
        ctk.CTkLabel(top_bar, text="VIEWING LOGS FOR:", font=FONT_SUBHEADER).pack(side="left", padx=(0, 10))
        self.log_selector = ctk.CTkOptionMenu(top_bar, values=["GLOBAL"], command=self.on_log_device_change, width=200)
        self.log_selector.pack(side="left", padx=(0, 20))
        self.log_selector.set("GLOBAL")

        self.log_device_count_label = ctk.CTkLabel(top_bar, text="📱 DEVICES: 0", font=("Roboto", 12, "bold"),
                                                   text_color=COLORS["warning"])
        self.log_device_count_label.pack(side="left", padx=(0, 15))
        self.log_shares_label = ctk.CTkLabel(top_bar, text="✅ SHARES: 0", font=("Roboto", 12, "bold"),
                                             text_color=COLORS["success"])
        self.log_shares_label.pack(side="left", padx=(0, 15))

        ctk.CTkButton(top_bar, text="🗑 Clear Selected", width=100, height=28, fg_color=COLORS["bg_card"],
                      border_width=1, border_color=COLORS["border"], command=self.clear_logs).pack(side="right")

        logs_container = ctk.CTkFrame(self.tab_logs, fg_color="transparent")
        logs_container.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        logs_container.grid_columnconfigure(0, weight=1)
        logs_container.grid_rowconfigure(0, weight=1)
        logs_container.grid_rowconfigure(1, weight=1)
        logs_container.grid_rowconfigure(2, weight=1)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background=COLORS["bg_card"], foreground=COLORS["text_main"],
                        fieldbackground=COLORS["bg_card"], borderwidth=0, rowheight=22, font=("Roboto", 10))
        style.map('Treeview', background=[('selected', COLORS["primary"])])
        style.configure("Treeview.Heading", background=COLORS["bg_lighter"], foreground=COLORS["text_main"],
                        font=("Roboto", 10, "bold"))

        f1 = ctk.CTkFrame(logs_container, fg_color="transparent")
        f1.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
        ctk.CTkLabel(f1, text="📝 MAIN LOGS", font=FONT_SUBHEADER, text_color=COLORS["primary"]).pack(anchor="w")
        tree_f1 = ctk.CTkFrame(f1, corner_radius=0, fg_color="transparent")
        tree_f1.pack(fill="both", expand=True)

        # --- MODIFIED COLUMNS FOR CAPTION ---
        cols1 = ("Time", "Device", "Link", "Caption", "Status")
        self.table_auto = ttk.Treeview(tree_f1, columns=cols1, show="headings", height=4)

        # Define widths and headings
        self.table_auto.heading("Time", text="TIME")
        self.table_auto.column("Time", width=80)
        self.table_auto.heading("Device", text="DEVICE")
        self.table_auto.column("Device", width=100)
        self.table_auto.heading("Link", text="LINK")
        self.table_auto.column("Link", width=200)
        self.table_auto.heading("Caption", text="CAPTION")
        self.table_auto.column("Caption", width=200)
        self.table_auto.heading("Status", text="STATUS")
        self.table_auto.column("Status", width=100)

        sb1 = ctk.CTkScrollbar(tree_f1, command=self.table_auto.yview)
        self.table_auto.configure(yscrollcommand=sb1.set)
        sb1.pack(side="right", fill="y")
        self.table_auto.pack(side="left", fill="both", expand=True)
        self.table_auto.tag_configure("SUCCESS", foreground=COLORS["success"])
        self.table_auto.tag_configure("ERROR", foreground=COLORS["danger"])
        self.table_auto.bind("<Double-1>", self.on_log_double_click)

        f2 = ctk.CTkFrame(logs_container, fg_color="transparent")
        f2.grid(row=1, column=0, sticky="nsew", pady=5)
        ctk.CTkLabel(f2, text="🐞 DEBUGGER", font=FONT_SUBHEADER, text_color="#A8A8A8").pack(anchor="w")
        tree_f2 = ctk.CTkFrame(f2, corner_radius=0, fg_color="transparent")
        tree_f2.pack(fill="both", expand=True)
        cols2 = ("Time", "Device", "Action", "Details")
        self.table_debug = ttk.Treeview(tree_f2, columns=cols2, show="headings", height=5)
        for c, w in zip(cols2, [80, 100, 150, 250]):
            self.table_debug.heading(c, text=c.upper())
            self.table_debug.column(c, width=w)
        sb2 = ctk.CTkScrollbar(tree_f2, command=self.table_debug.yview)
        self.table_debug.configure(yscrollcommand=sb2.set)
        sb2.pack(side="right", fill="y")
        self.table_debug.pack(side="left", fill="both", expand=True)
        self.table_debug.tag_configure("INFO", foreground="#8B949E")

        f3 = ctk.CTkFrame(logs_container, fg_color="transparent")
        f3.grid(row=2, column=0, sticky="nsew", pady=(5, 0))
        ctk.CTkLabel(f3, text="⚙️ SYSTEM", font=FONT_SUBHEADER, text_color=COLORS["warning"]).pack(anchor="w")
        tree_f3 = ctk.CTkFrame(f3, corner_radius=0, fg_color="transparent")
        tree_f3.pack(fill="both", expand=True)
        cols3 = ("Time", "Device", "Message")
        self.table_sys = ttk.Treeview(tree_f3, columns=cols3, show="headings", height=3)
        for c, w in zip(cols3, [80, 100, 400]):
            self.table_sys.heading(c, text=c.upper())
            self.table_sys.column(c, width=w)
        sb3 = ctk.CTkScrollbar(tree_f3, command=self.table_sys.yview)
        self.table_sys.configure(yscrollcommand=sb3.set)
        sb3.pack(side="right", fill="y")
        self.table_sys.pack(side="left", fill="both", expand=True)
        self.table_sys.tag_configure("INFO", foreground="#4FC3F7")
        self.table_sys.tag_configure("WARN", foreground=COLORS["warning"])
        self.table_sys.tag_configure("ERROR", foreground=COLORS["danger"])

    def on_log_device_change(self, choice):
        self.current_log_device = choice
        self.refresh_log_tables()

    def refresh_log_tables(self):
        for item in self.table_auto.get_children():
            self.table_auto.delete(item)
        for item in self.table_debug.get_children():
            self.table_debug.delete(item)
        for item in self.table_sys.get_children():
            self.table_sys.delete(item)
        target = self.current_log_device
        for entry in self.log_storage["auto"]:
            # Entry format now: (ts, dev, link, caption, status, level)
            if target == "GLOBAL" or entry[1] == target:
                self.table_auto.insert("", "end", values=(entry[0], entry[1], entry[2], entry[3], entry[4]),
                                       tags=(entry[5],))
        for entry in self.log_storage["debug"]:
            if target == "GLOBAL" or entry[1] == target:
                self.table_debug.insert("", "end", values=entry)
        for entry in self.log_storage["sys"]:
            if target == "GLOBAL" or entry[1] == target:
                self.table_sys.insert("", "end", values=(entry[0], entry[1], entry[2]), tags=(entry[3],))
        if self.table_auto.get_children():
            self.table_auto.see(self.table_auto.get_children()[-1])
        if self.table_debug.get_children():
            self.table_debug.see(self.table_debug.get_children()[-1])
        if self.table_sys.get_children():
            self.table_sys.see(self.table_sys.get_children()[-1])

    def log_row(self, device, link, caption, status, level="INFO"):
        ts = self.get_manila_time()
        d_name = device[:8] if device else "SYSTEM"
        if "SUCCESS" in status.upper():
            level = "SUCCESS"
        elif "FAIL" in status.upper() or "ERROR" in status.upper():
            level = "ERROR"
        is_sys = any(x in status.upper() for x in
                     ["REBOOT", "ADB", "CRASH", "WIFI", "AIRPLANE", "INSTALL", "SYSTEM", "NEW DEVICE", "WAITING",
                      "UNLOCKING", "PREPARING"])

        if is_sys:
            self.log_storage["sys"].append((ts, d_name, status, level))
            if self.current_log_device == "GLOBAL" or self.current_log_device == d_name:
                self.after(0, lambda: self._safe_insert(self.table_sys, (ts, d_name, status), level))
        else:
            # Shorten Link and Caption for display
            disp_link = (link[:30] + '...') if len(link) > 30 else link
            disp_cap = (caption[:30] + '...') if caption and len(caption) > 30 else caption
            if not disp_cap: disp_cap = "---"

            self.log_storage["auto"].append((ts, d_name, disp_link, disp_cap, status, level))
            if self.current_log_device == "GLOBAL" or self.current_log_device == d_name:
                self.after(0,
                           lambda: self._safe_insert(self.table_auto, (ts, d_name, disp_link, disp_cap, status), level))

    def log_debug(self, device, action, details):
        ts = datetime.now().strftime("%H:%M:%S")
        d_name = device[:8] if device else "SYSTEM"
        self.log_storage["debug"].append((ts, d_name, action, details))
        if len(self.log_storage["debug"]) > 1000:
            self.log_storage["debug"].pop(0)
        if self.current_log_device == "GLOBAL" or self.current_log_device == d_name:
            self.after(0, lambda: self._safe_insert(self.table_debug, (ts, d_name, action, details), "INFO"))

    def _safe_insert(self, tree, values, tag):
        try:
            item = tree.insert("", "end", values=values, tags=(tag,))
            tree.see(item)
            if len(tree.get_children()) > 200:
                tree.delete(tree.get_children()[0])
        except:
            pass

    def clear_logs(self):
        if self.current_log_device == "GLOBAL":
            self.log_storage["auto"] = []
            self.log_storage["debug"] = []
            self.log_storage["sys"] = []
        else:
            t = self.current_log_device
            self.log_storage["auto"] = [x for x in self.log_storage["auto"] if x[1] != t]
            self.log_storage["debug"] = [x for x in self.log_storage["debug"] if x[1] != t]
            self.log_storage["sys"] = [x for x in self.log_storage["sys"] if x[1] != t]
        self.refresh_log_tables()

    def refresh_devices(self):
        try:
            CREATE_NO_WINDOW = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            o = subprocess.check_output(["adb", "devices"], creationflags=CREATE_NO_WINDOW).decode("utf-8")
            current_devices = [l.split()[0] for l in o.strip().split("\n")[1:] if
                               "device" in l and not l.startswith("*")]
            self.devices = current_devices
            self.device_count_label.configure(text=f"Connected: {len(self.devices)}")

            dropdown_values = ["GLOBAL"] + [d[:8] for d in self.devices]
            self.log_selector.configure(values=dropdown_values)

            run_values = [d for d in self.devices] if self.devices else ["No Devices"]
            self.dash_device_select.configure(values=run_values)
            if self.devices and self.dash_device_select.get() == "Select Device":
                self.dash_device_select.set(self.devices[0])

            if not self.is_running:
                self.overall_stats.update_devices(len(self.devices))

            if hasattr(self, 'log_device_count_label'):
                self.log_device_count_label.configure(text=f"📱 DEVICES: {len(self.devices)}")

            for widget in self.device_config_frame.winfo_children():
                widget.destroy()
            self.device_widgets = []
            if not self.devices:
                ctk.CTkLabel(self.device_config_frame, text="No Devices Connected", text_color="#666",
                             font=FONT_BODY).pack(pady=20)
                return
            for device in self.devices:
                device_frame = DeviceFrame(self.device_config_frame, device)
                device_frame.pack(fill="x", padx=10, pady=5)
                self.device_widgets.append(device_frame)
                threading.Thread(target=self.get_device_info, args=(device, device_frame), daemon=True).start()
        except:
            pass

    def setup_adb(self):
        c = ctk.CTkFrame(self.tab_adb, fg_color="transparent")
        c.pack(fill="both", expand=True, padx=20, pady=20)
        f1 = ctk.CTkFrame(c, fg_color=COLORS["bg_card"], corner_radius=10)
        f1.pack(fill="x", pady=10)
        ctk.CTkLabel(f1, text="BATCH ACTIONS", font=FONT_SUBHEADER, text_color=COLORS["primary"]).pack(anchor="w",
                                                                                                       padx=15, pady=10)
        b1 = ctk.CTkFrame(f1, fg_color="transparent")
        b1.pack(fill="x", padx=15, pady=5)
        ctk.CTkButton(b1, text="✈️ Airplane ON", height=35, fg_color=COLORS["warning"], text_color="#000",
                      command=lambda: self.toggle_airplane_mode(True)).pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkButton(b1, text="✈️ Airplane OFF", height=35, fg_color=COLORS["success"],
                      command=lambda: self.toggle_airplane_mode(False)).pack(side="left", fill="x", expand=True, padx=5)
        f2 = ctk.CTkFrame(c, fg_color=COLORS["bg_card"], corner_radius=10)
        f2.pack(fill="x", pady=10)
        ctk.CTkLabel(f2, text="APK INSTALL", font=FONT_SUBHEADER, text_color=COLORS["primary"]).pack(anchor="w",
                                                                                                     padx=15, pady=10)
        b2 = ctk.CTkFrame(f2, fg_color="transparent")
        b2.pack(fill="x", padx=15, pady=5)
        self.apk_entry = ctk.CTkEntry(b2)
        self.apk_entry.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkButton(b2, text="📂", width=40, command=self.browse_apk).pack(side="left", padx=5)
        ctk.CTkButton(b2, text="Install All", width=100, command=self.install_apk_all).pack(side="left", padx=5)
        f3 = ctk.CTkFrame(c, fg_color=COLORS["bg_card"], corner_radius=10)
        f3.pack(fill="x", pady=10)
        ctk.CTkLabel(f3, text="WIRELESS ADB", font=FONT_SUBHEADER, text_color=COLORS["primary"]).pack(anchor="w",
                                                                                                      padx=15, pady=10)
        b3 = ctk.CTkFrame(f3, fg_color="transparent")
        b3.pack(fill="x", padx=15, pady=5)
        ctk.CTkButton(b3, text="Connect All (WIFI)", height=35, fg_color=COLORS["success"],
                      command=self.enable_wireless_adb).pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkButton(b3, text="Disconnect All", height=35, fg_color=COLORS["danger"],
                      command=self.disconnect_wireless_adb).pack(side="left", fill="x", expand=True, padx=5)

    def on_log_double_click(self, event):
        try:
            tree = event.widget
            item = tree.item(tree.identify_row(event.y))
            url = item['values'][2]
            if "http" in url:
                webbrowser.open(url)
        except:
            pass

    def on_close(self):
        self.destroy()
        os._exit(0)

    def get_manila_time(self):
        return datetime.now().strftime("%I:%M:%S %p")

    def browse_driver(self):
        f = filedialog.askopenfilename(filetypes=[("Exe", "*.exe")])
        if f:
            self.driver_entry.delete(0, "end")
            self.driver_entry.insert(0, f)
            self.chrome_driver_path = f

    def browse_global_cookie(self):
        f = filedialog.askopenfilename(filetypes=[("Txt", "*.txt")])
        if f:
            self.cookie_entry.delete(0, "end")
            self.cookie_entry.insert(0, f)
            self.global_cookie_path = f

    def browse_apk(self):
        f = filedialog.askopenfilename(filetypes=[("APK", "*.apk")])
        if f:
            self.apk_entry.delete(0, "end")
            self.apk_entry.insert(0, f)

    def load_settings(self):
        try:
            with open("device_settings.json", "r") as f:
                d = json.load(f)
                self.chrome_driver_path = d.get("chrome_driver_path", "chromedriver.exe")
                self.global_cookie_path = d.get("global_cookie_path", "")
                self.after(500, lambda: self._set_vals(d))
        except:
            pass

    def _set_vals(self, d):
        try:
            self.cookie_limit_entry.delete(0, "end")
            self.cookie_limit_entry.insert(0, d.get("cookie_limit", "0"))
            self.min_delay.delete(0, "end")
            self.min_delay.insert(0, d.get("min_delay", "5"))
            self.max_delay.delete(0, "end")
            self.max_delay.insert(0, d.get("max_delay", "10"))
            self.dash_pre_delay.delete(0, "end")
            self.dash_pre_delay.insert(0, d.get("dash_pre_delay", "10"))
            self.dash_post_delay.delete(0, "end")
            self.dash_post_delay.insert(0, d.get("dash_post_delay", "10"))
            self.retry_count.delete(0, "end")
            self.retry_count.insert(0, d.get("retry_count", "3"))
            self.stagger_var.set(d.get("slow_start_enabled", True))
            self.stagger_delay_entry.delete(0, "end")
            self.stagger_delay_entry.insert(0, d.get("slow_start_delay", "8"))
        except:
            pass

    def save_config(self):
        self.chrome_driver_path = self.driver_entry.get()
        self.global_cookie_path = self.cookie_entry.get()
        self.saved_settings = {
            "chrome_driver_path": self.chrome_driver_path,
            "global_cookie_path": self.global_cookie_path,
            "cookie_limit": self.cookie_limit_entry.get(),
            "min_delay": self.min_delay.get(), "max_delay": self.max_delay.get(),
            "retry_count": self.retry_count.get(),
            "dash_pre_delay": self.dash_pre_delay.get(), "dash_post_delay": self.dash_post_delay.get(),
            "slow_start_enabled": self.stagger_var.get(), "slow_start_delay": self.stagger_delay_entry.get()
        }
        with open("device_settings.json", "w") as f:
            json.dump(self.saved_settings, f, indent=2)
        messagebox.showinfo("Saved", "Configuration updated.")

    def add_pair(self):
        pair_num = len(self.pair_widgets) + 1
        new_pair = PairFrame(self.pairs_scroll, pair_num, lambda: self.remove_pair(new_pair))
        new_pair.pack(fill="x", padx=5, pady=5)
        self.pair_widgets.append(new_pair)

    def remove_pair(self, frame):
        if len(self.pair_widgets) > 1:
            frame.destroy()
            self.pair_widgets.remove(frame)
            for i, f in enumerate(self.pair_widgets):
                f.header_label.configure(text=f"📍 LINK #{i + 1}")

    def get_device_info(self, device_id, device_frame):
        try:
            CREATE_NO_WINDOW = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            model = subprocess.run(["adb", "-s", device_id, "shell", "getprop", "ro.product.model"],
                                   capture_output=True, text=True, creationflags=CREATE_NO_WINDOW).stdout.strip()
            ver = subprocess.run(["adb", "-s", device_id, "shell", "getprop", "ro.build.version.release"],
                                 capture_output=True, text=True, creationflags=CREATE_NO_WINDOW).stdout.strip()
            self.after(100, lambda: device_frame.update_device_info(model, ver))
        except:
            pass

    def parse_cookies(self, cookie_str):
        cookies = []
        for pair in cookie_str.split(";"):
            if "=" in pair:
                name, value = pair.strip().split("=", 1)
                cookies.append({"name": name, "value": value, "domain": ".facebook.com"})
        return cookies

    def unlock_device_sequence(self, device_id):
        CREATE_NO_WINDOW = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        try:
            self.log_debug(device_id, "ADB", "Wake Screen")
            subprocess.run(["adb", "-s", device_id, "shell", "input", "keyevent", "224"],
                           creationflags=CREATE_NO_WINDOW)
            time.sleep(0.5)
            self.log_debug(device_id, "ADB", "Swipe Unlock")
            subprocess.run(["adb", "-s", device_id, "shell", "input", "swipe", "200", "500", "200", "0", "300"],
                           creationflags=CREATE_NO_WINDOW)
            time.sleep(1)
            subprocess.run(["adb", "-s", device_id, "shell", "input", "keyevent", "3"], creationflags=CREATE_NO_WINDOW)
        except:
            pass

    def run_fb_automation(self, device_id):
        self.log_row(device_id, "---", "---", "🚀 INIT: PREPARING...", "INFO")
        self.unlock_device_sequence(device_id)

        options = Options()
        options.add_experimental_option("androidPackage", "com.android.chrome")
        options.add_experimental_option("androidDeviceSerial", device_id)
        for arg in [
            "--blink-settings=imagesEnabled=false,videoAutoplayEnabled=false",
            "--disable-notifications",
            "--no-sandbox",
            "--mute-audio",
            "--disable-popup-blocking",
            "--disable-infobars"
            "--blink-settings=imagesEnabled=false,videoAutoplayEnabled=false",  # Iwas load ng heavy media
            "--disable-notifications",
            "--disable-dev-shm-usage",  # Importante: Iwas memory crash sa Linux/Android environment
            # "--disable-gpu",  # Iwas GPU errors
            "--disable-extensions",  # Bawas memory usage
            "--disable-infobars",
            "--ignore-certificate-errors"
            "--renderer-process-limit=1",  # Lilimitahan ang Chrome sa 1 process lang
            "--single-process",
            "--disable-background-networking",
            "--disable-sync",
            "--disable-translate"
            "--disk-cache-size=1"
            "--media-cache-size=1"
        ]:
            options.add_argument(arg)
        options.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])

        service = ChromeService(executable_path=self.chrome_driver_path, log_output=os.devnull)
        CREATE_NO_WINDOW = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0

        try:
            pre_wait = float(self.dash_pre_delay.get())
        except:
            pre_wait = 5.0
        try:
            limit = int(self.cookie_limit_entry.get())
        except:
            limit = 0

        processed = 0
        while self.is_running:
            if limit > 0 and processed >= limit:
                self.log_row(device_id, "---", "---", "⛔ LIMIT REACHED", "WARN")
                break
            try:
                data = self.cookie_queue.get(timeout=2)
                cookie_str = data['cookie']
                acc_idx = data['index']
            except queue.Empty:
                if self.cookie_queue.empty():
                    break
                continue

            driver = None
            processed += 1
            try:
                self.log_debug(device_id, "ADB", "Clear Chrome")
                subprocess.run(["adb", "-s", device_id, "shell", "input", "keyevent", "224"])
                time.sleep(2)
                subprocess.run(["adb", "-s", device_id, "shell", "pm", "clear", "com.android.chrome"],capture_output=True, creationflags=CREATE_NO_WINDOW)
                time.sleep(2)

                self.log_debug(device_id, "DRIVER", "Start Chrome")
                driver = webdriver.Chrome(service=service, options=options)
                self.active_drivers.append(driver)
                wait = WebDriverWait(driver, 20)

                self.log_debug(device_id, "NAV", "Facebook.com")
                blocked_urls = [
                    "*.jpg", "*.jpeg", "*.png", "*.gif",  # Images/GIFs
                    "*.css",  # Styles (Nakakapagpabagal din ito)
                    "*.mp4", "*.avi",  # Videos
                    "*.woff", "*.woff2", "*.ttf",  # Fonts (Icons)
                    "*.ico",  # Favicons
                    "*favicon*",
                ]

                # I-enable ang Network Tracking
                driver.execute_cdp_cmd("Network.enable", {})

                # I-set ang blocking rules
                driver.execute_cdp_cmd("Network.setBlockedURLs", {"urls": blocked_urls})

                driver.get("https://m.facebook.com")
                self.log_debug(device_id, "COOKIE", f"Inject #{acc_idx}")
                for c in self.parse_cookies(cookie_str):
                    try:
                        driver.add_cookie(c)
                    except:
                        pass
                driver.refresh()

                self.log_debug(device_id, "CHECK", "Login Status")
                try:
                    wait.until(EC.presence_of_element_located((By.XPATH,
                                                               "//div[@aria-label=\"What's on your mind?\"] | //div[@role='feed'] | //a[contains(@href, 'messages')]")))
                except:
                    if "facebook.com" in driver.current_url:
                        raise Exception("Checkpoint/Login Fail")
                    continue
                self.log_debug(device_id, "LOGIN", "Success")
                time.sleep(3)

                for ln, (link, cap_file) in enumerate(self.job_list_global, 1):
                    if not self.is_running:
                        break
                    sel_cap = "---"
                    success = False
                    for attempt in range(3):
                        if not self.is_running:
                            break
                        try:
                            self.log_debug(device_id, "NAV", f"Link #{ln}")
                            driver.get("https://m.facebook.com/composer/")

                            self.log_debug(device_id, "FIND", "Textbox")
                            box = wait.until(
                                EC.element_to_be_clickable((By.XPATH, "//div[@role='textbox'] | //textarea")))
                            box.click()
                            time.sleep(1)

                            self.log_debug(device_id, "TYPE", "URL")
                            box.send_keys(link)
                            self.log_debug(device_id, "WAIT", "Preview (15s)")
                            time.sleep(15)

                            self.log_debug(device_id, "CLEAN", "Text")
                            try:
                                box.send_keys(Keys.CONTROL, "a")
                                time.sleep(0.2)
                                box.send_keys(Keys.BACK_SPACE)
                            except:
                                driver.execute_script("arguments[0].value = '';", box)

                            if cap_file and os.path.exists(cap_file):
                                try:
                                    with open(cap_file, "r", encoding="utf-8") as f:
                                        lines = [x.strip() for x in f if x.strip()]
                                    if lines:
                                        sel_cap = random.choice(lines)
                                        self.log_debug(device_id, "TYPE", "Caption")
                                        box.send_keys(sel_cap)
                                        time.sleep(pre_wait)
                                except:
                                    pass

                            self.log_debug(device_id, "FIND", "Post Btn")
                            post_xpath = "//button[@name='view_post'] | //button[@value='Post'] | //input[@value='Post'] | //div[translate(@aria-label, 'POST', 'post')='post'] | //span[translate(text(), 'POST', 'post')='post']"
                            post_btn = wait.until(EC.presence_of_element_located((By.XPATH, post_xpath)))
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", post_btn)
                            time.sleep(2)

                            self.log_debug(device_id, "CLICK", "Post (JS)")
                            driver.execute_script("arguments[0].click();", post_btn)

                            self.log_debug(device_id, "WAIT", "Finalizing (15s)")
                            time.sleep(15)

                            self.log_row(device_id, link, sel_cap, f"SUCCESS [LINK {ln}][Acc#{acc_idx}]", "SUCCESS")
                            self.total_shares += 1
                            self.total_attempts += 1
                            self.update_stats()
                            success = True
                            break
                        except Exception:
                            self.log_debug(device_id, "RETRY", f"{attempt + 1}/3")
                            time.sleep(2)
                            try:
                                driver.refresh()
                            except:
                                pass

                    if not success:
                        self.log_row(device_id, link, "---", f"FAILED [LINK {ln}] - NEXT ACCOUNT", "ERROR")
                        self.total_attempts += 1
                        self.update_stats()
                        break

                    try:
                        d = random.randint(int(self.min_delay.get()), int(self.max_delay.get()))
                    except:
                        d = 5
                    self.log_debug(device_id, "SLEEP", f"{d}s")
                    time.sleep(d)

                if driver in self.active_drivers:
                    self.active_drivers.remove(driver)
                driver.quit()
                self.log_debug(device_id, "DONE", "Account Finished")
            except Exception as e:
                self.log_row(device_id, "---", "---", f"ERROR: {str(e)[:30]}", "ERROR")
                if driver:
                    try:
                        driver.quit()
                    except:
                        pass
            finally:
                if self.is_running:
                    try:
                        self.cookie_queue.task_done()
                    except:
                        pass

        if device_id in self.active_devices_set:
            self.active_devices_set.remove(device_id)
            self.after(0, lambda: self.overall_stats.update_devices(len(self.active_devices_set)))

    def update_stats(self):
        self.after(0, lambda: self.overall_stats.update_stats(self.total_shares, self.error_count))
        if hasattr(self, 'log_shares_label'):
            self.after(0, lambda: self.log_shares_label.configure(text=f"✅ SHARES: {self.total_shares}"))

    def start_threads(self):
        if not self.devices:
            messagebox.showerror("Error", "No devices connected!")
            return
        self.job_list_global = [(p.link_entry.get(), p.caption_path.get()) for p in self.pair_widgets if
                                p.link_entry.get().strip()]
        if not self.job_list_global:
            messagebox.showerror("Error", "No links configured!")
            return
        if not os.path.exists(self.cookie_entry.get()):
            messagebox.showerror("Error", "Invalid Cookie File!")
            return

        try:
            with open(self.cookie_entry.get(), "r") as f:
                ac = [l.strip() for l in f if l.strip()]
            if not ac:
                raise Exception
        except:
            messagebox.showerror("Error", "Cookie file empty/error!")
            return

        with self.cookie_queue.mutex:
            self.cookie_queue.queue.clear()
        for i, c in enumerate(ac):
            self.cookie_queue.put({'cookie': c, 'index': i + 1})

        self.is_running = True
        self.status_badge.configure(text="● RUNNING", text_color=COLORS["success"])
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.tabview.set(" System Logs ")
        self.active_devices_set = set()

        try:
            stag = float(self.stagger_delay_entry.get())
        except:
            stag = 8.0
        use_stag = self.stagger_var.get()

        def seq():
            if self.single_dev_var.get():
                target_dev = self.dash_device_select.get()
                if target_dev and target_dev in self.devices:
                    target_list = [target_dev]
                else:
                    self.log_row("SYSTEM", "---", "---", "Invalid Target Device!", "ERROR")
                    target_list = []
            else:
                target_list = self.devices

            for i, dev in enumerate(target_list):
                if not self.is_running:
                    break

                self.active_devices_set.add(dev)
                threading.Thread(target=self.run_fb_automation, args=(dev,)).start()
                self.after(0, lambda: self.overall_stats.update_devices(len(self.active_devices_set)))

                if use_stag and i < len(target_list) - 1:
                    self.log_row(dev, "---", "---", f"STARTING (Next in {stag}s)...", "INFO")
                    time.sleep(stag)
                else:
                    self.log_row(dev, "---", "---", "STARTING...", "INFO")

            while self.is_running and not self.cookie_queue.empty():
                time.sleep(2)
            time.sleep(5)
            self.is_running = False
            self.after(0, lambda: [self.start_btn.configure(state="normal"), self.stop_btn.configure(state="disabled"),
                                   self.status_badge.configure(text="● IDLE", text_color=COLORS["text_sub"])])

        threading.Thread(target=seq, daemon=True).start()

    def stop_automation(self):
        self.is_running = False
        self.stop_btn.configure(state="disabled")
        self.status_badge.configure(text="● STOPPING...", text_color=COLORS["danger"])
        with self.cookie_queue.mutex:
            self.cookie_queue.queue.clear()

        def kill():
            for d in list(self.active_drivers):
                try:
                    d.quit()
                except:
                    pass
            self.active_drivers = []
            create_no_window = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            if os.name == 'nt':
                subprocess.run(["taskkill", "/F", "/IM", "chromedriver.exe", "/T"], creationflags=create_no_window,
                               capture_output=True)
            else:
                subprocess.run(["pkill", "-9", "chromedriver"], capture_output=True)
            for dev in self.devices:
                subprocess.run(["adb", "-s", dev, "shell", "am", "force-stop", "com.android.chrome"],
                               creationflags=create_no_window, capture_output=True)
            self.after(0, lambda: messagebox.showinfo("Stopped", "Automation Force Stopped."))

        threading.Thread(target=kill, daemon=True).start()

    def toggle_airplane_mode(self, state):
        v = "1" if state else "0"
        vb = "true" if state else "false"
        create_no_window = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0

        def t():
            for d in self.devices:
                subprocess.run(["adb", "-s", d, "shell", "settings", "put", "global", "airplane_mode_on", v],
                               creationflags=create_no_window)
                subprocess.run(
                    ["adb", "-s", d, "shell", "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE", "--ez",
                     "state", vb], creationflags=create_no_window)
                self.log_row(d, "---", "---", f"AIRPLANE {state}", "INFO")
            messagebox.showinfo("Done", f"Airplane Mode {'ON' if state else 'OFF'}")

        threading.Thread(target=t, daemon=True).start()

    def install_apk_all(self):
        p = self.apk_entry.get()
        if not os.path.exists(p):
            messagebox.showerror("Error", "Invalid APK")
            return
        create_no_window = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0

        def t():
            for d in self.devices:
                self.log_row(d, "---", "---", "INSTALLING APK...", "INFO")
                subprocess.run(["adb", "-s", d, "install", "-r", p], creationflags=create_no_window)
                self.log_row(d, "---", "---", "APK INSTALLED", "SUCCESS")
            messagebox.showinfo("Done", "Batch Install Complete")

        threading.Thread(target=t, daemon=True).start()

    def enable_wireless_adb(self):
        create_no_window = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0

        def t():
            for d in self.devices:
                if ":" in d:
                    continue
                subprocess.run(["adb", "-s", d, "tcpip", "5555"], creationflags=create_no_window)
                time.sleep(2)
                try:
                    ip = subprocess.check_output(["adb", "-s", d, "shell", "ip", "addr", "show", "wlan0"],
                                                 creationflags=create_no_window).decode().split("inet ")[1].split("/")[
                        0]
                    subprocess.run(["adb", "connect", f"{ip}:5555"], creationflags=create_no_window)
                    self.log_row(d, "---", "---", f"WIFI CONNECTED {ip}", "SUCCESS")
                except:
                    self.log_row(d, "---", "---", "WIFI FAIL", "ERROR")
            self.after(2000, self.refresh_devices)

        threading.Thread(target=t, daemon=True).start()

    def disconnect_wireless_adb(self):
        subprocess.run(["adb", "disconnect"], creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        self.after(1000, self.refresh_devices)

    def system_full_reset(self):
        create_no_window = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        if os.name == 'nt':
            subprocess.run(["taskkill", "/F", "/IM", "chromedriver.exe", "/T"], creationflags=create_no_window,
                           capture_output=True)
        for d in self.devices:
            subprocess.run(["adb", "-s", d, "shell", "pm", "clear", "com.android.chrome"],
                           creationflags=create_no_window, capture_output=True)
        subprocess.run(["adb", "kill-server"], creationflags=create_no_window)
        time.sleep(1)
        subprocess.run(["adb", "start-server"], creationflags=create_no_window)
        self.refresh_devices()

    def action_go_home(self):
        create_no_window = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0

        def t():
            for d in self.devices:
                subprocess.run(["adb", "-s", d, "shell", "input", "keyevent", "224"], creationflags=create_no_window)
                subprocess.run(["adb", "-s", d, "shell", "input", "swipe", "300", "1000", "300", "500"],
                               creationflags=create_no_window)

        threading.Thread(target=t, daemon=True).start()

    def action_home_only(self):
        create_no_window = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0

        def t():
            for d in self.devices:
                subprocess.run(["adb", "-s", d, "shell", "input", "keyevent", "3"], creationflags=create_no_window)

        threading.Thread(target=t, daemon=True).start()

    def action_stay_awake(self):
        create_no_window = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0

        def t():
            for d in self.devices:
                subprocess.run(["adb", "-s", d, "shell", "svc", "power", "stayon", "true"],
                               creationflags=create_no_window)
                subprocess.run(["adb", "-s", d, "shell", "input", "keyevent", "224"], creationflags=create_no_window)

        threading.Thread(target=t, daemon=True).start()

    def reboot_all_devices(self):
        if not messagebox.askyesno("Reboot", "Reboot ALL connected devices?"):
            return
        create_no_window = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0

        def t():
            for d in self.devices:
                subprocess.Popen(["adb", "-s", d, "reboot"], creationflags=create_no_window)

        threading.Thread(target=t, daemon=True).start()


if __name__ == "__main__":
    app = FacebookAutomationGUI()
    app.mainloop()
