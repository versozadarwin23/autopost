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
import webbrowser  # ADDED FOR CLICKABLE LINKS
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from datetime import datetime

__version__ = "2"  # Incremented version locally
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

FONT_HEADER = ("Roboto", 22, "bold")
FONT_SUBHEADER = ("Roboto", 15, "bold")
FONT_BODY = ("Roboto", 13)
FONT_MONO = ("Consolas", 12)


class StatCard(ctk.CTkFrame):
    def __init__(self, parent, title, value, icon, color):
        super().__init__(parent, fg_color=COLORS["bg_card"], corner_radius=15,
                         border_width=1, border_color=COLORS["border"])
        self.value_var = ctk.StringVar(value=str(value))
        self.icon_label = ctk.CTkLabel(self, text=icon, font=("Segoe UI Emoji", 24))
        self.icon_label.place(relx=0.85, rely=0.25, anchor="center")
        self.title_label = ctk.CTkLabel(self, text=title.upper(), font=("Roboto", 11, "bold"),
                                        text_color=COLORS["text_sub"])
        self.title_label.pack(anchor="w", padx=15, pady=(12, 0))
        self.value_label = ctk.CTkLabel(self, textvariable=self.value_var, font=("Roboto", 28, "bold"),
                                        text_color=color)
        self.value_label.pack(anchor="w", padx=15, pady=(2, 12))

    def update_value(self, new_value):
        self.value_var.set(str(new_value))


class StatsFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        title = ctk.CTkLabel(self, text="📊 LIVE ANALYTICS", font=FONT_SUBHEADER, text_color=COLORS["primary"])
        title.pack(anchor="w", pady=(0, 10))
        self.grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True)
        self.grid_frame.grid_columnconfigure((0, 1), weight=1)

        self.card_shares = StatCard(self.grid_frame, "Total Shares", "0", "🚀", COLORS["success"])
        self.card_shares.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="ew")

        self.card_failed = StatCard(self.grid_frame, "Failed", "0", "⚠️", COLORS["danger"])
        self.card_failed.grid(row=0, column=1, padx=(5, 0), pady=5, sticky="ew")

        self.card_devices = StatCard(self.grid_frame, "Active Devices", "0", "📱", COLORS["warning"])
        self.card_devices.grid(row=1, column=0, columnspan=2, padx=0, pady=(5, 5), sticky="ew")

    def update_stats(self, shares, failed):
        self.card_shares.update_value(shares)
        self.card_failed.update_value(failed)

    def update_devices(self, count):
        self.card_devices.update_value(count)


class DeviceFrame(ctk.CTkFrame):
    def __init__(self, parent, device_id):
        super().__init__(parent, fg_color=COLORS["bg_card"], corner_radius=12,
                         border_width=1, border_color=COLORS["border"])
        self.device_id = device_id
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=15)
        self.device_label = ctk.CTkLabel(header_frame, text=f"📱 {device_id}", font=("Roboto", 14, "bold"),
                                         text_color=COLORS["primary"])
        self.device_label.pack(side="left")
        self.info_label = ctk.CTkLabel(header_frame, text="Syncing...", font=FONT_BODY,
                                       text_color=COLORS["text_sub"])
        self.info_label.pack(side="right")

    def update_device_info(self, model, version):
        info_text = f"{model} • Android {version}"
        self.info_label.configure(text=info_text)


class PairFrame(ctk.CTkFrame):
    def __init__(self, parent, pair_num, on_remove):
        super().__init__(parent, fg_color=COLORS["bg_lighter"], corner_radius=12,
                         border_width=1, border_color=COLORS["border"])
        self.on_remove = on_remove

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 5))
        self.header_label = ctk.CTkLabel(header, text=f"📍 LINK #{pair_num}", font=("Roboto", 14, "bold"),
                                         text_color=COLORS["primary"])
        self.header_label.pack(side="left")

        if pair_num > 1:
            btn_del = ctk.CTkButton(header, text="✖", width=30, height=30, fg_color="transparent",
                                    hover_color=COLORS["danger"], text_color=COLORS["text_sub"], corner_radius=8,
                                    command=self.remove)
            btn_del.pack(side="right")

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkLabel(content, text="Target Link / URL", font=("Roboto", 12, "bold"),
                     text_color=COLORS["text_sub"]).pack(
            anchor="w", pady=(5, 5))
        self.link_entry = ctk.CTkEntry(content, height=40, placeholder_text="e.g., https://facebook.com/...",
                                       fg_color=COLORS["bg_main"], border_color=COLORS["border"], corner_radius=8)
        self.link_entry.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(content, text="Caption File (.txt)", font=("Roboto", 12, "bold"),
                     text_color=COLORS["text_sub"]).pack(
            anchor="w", pady=(0, 5))
        cap_row = ctk.CTkFrame(content, fg_color="transparent")
        cap_row.pack(fill="x")
        self.caption_path = ctk.CTkEntry(cap_row, height=40, placeholder_text="Select caption file...",
                                         fg_color=COLORS["bg_main"], border_color=COLORS["border"], corner_radius=8)
        self.caption_path.pack(side="left", fill="x", expand=True, padx=(0, 10))

        btn_browse = ctk.CTkButton(cap_row, text="Browse", width=80, height=40, fg_color=COLORS["bg_card"],
                                   hover_color=COLORS["primary"], border_width=1, border_color=COLORS["border"],
                                   font=("Roboto", 13, "bold"), corner_radius=8,
                                   command=self.browse_caption)
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

        self.title(f"AutoPost V{__version__}")
        self.geometry("1280x800")
        self.after(0, lambda: self.state("zoomed"))
        self.configure(fg_color=COLORS["bg_main"])

        self.is_running = False
        self.chrome_driver_path = "chromedriver.exe"
        self.global_cookie_path = ""
        self.devices = []
        self.device_resolutions = {}
        self.device_widgets = []
        self.pair_widgets = []
        self.total_shares = 0
        self.error_count = 0
        self.total_attempts = 0
        self.start_time = None
        self.all_logs = []
        self.saved_settings = {}

        threading.Thread(target=self.device_monitor_thread, daemon=True).start()

        self.load_settings()
        self.layout_ui()
        self.refresh_devices()
        self.check_for_updates()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def check_for_updates(self):
        def _check():
            try:
                req = urllib.request.Request(VERSION_CHECK_URL, headers={'Cache-Control': 'no-cache'})
                with urllib.request.urlopen(req, timeout=5) as response:
                    remote_version = response.read().decode('utf-8').strip()

                if remote_version and remote_version != __version__:
                    self.after(0, lambda: self.show_update_popup(remote_version))
            except:
                pass

        threading.Thread(target=_check, daemon=True).start()

    def show_update_popup(self, remote_version):
        msg = f"A new update is available! (Version V{remote_version})\n\nWould you like to download and install the update now? The program will close and restart automatically."
        if messagebox.askyesno("System Update", msg):
            self.perform_update()

    def perform_update(self):
        self.status_badge.configure(text="● DOWNLOADING UPDATE...", text_color=COLORS["warning"])

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

                bat_code = f"""@echo off
echo Updating AutoPost... Please do not close this window.
timeout /t 3 /nobreak >nul
move /y main_update.py "{script_name}"
start python "{script_name}"
del "%~f0"
"""
                with open("updater.bat", "w") as f:
                    f.write(bat_code)

                subprocess.Popen("updater.bat", creationflags=subprocess.CREATE_NEW_CONSOLE)

                self.after(0, self.on_close)

            except:
                self.after(0, lambda: messagebox.showerror("Update Error", f"Failed to download the update: {e}"))
                self.after(0, lambda: self.status_badge.configure(text="● IDLE", text_color=COLORS["text_sub"]))

        threading.Thread(target=_download_and_replace, daemon=True).start()

    def device_monitor_thread(self):
        while True:
            try:
                CREATE_NO_WINDOW = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                o = subprocess.check_output(["adb", "devices"], creationflags=CREATE_NO_WINDOW).decode("utf-8")
                current_devices = [l.split()[0] for l in o.strip().split("\n")[1:] if
                                   "device" in l and not l.startswith("*")]

                if set(current_devices) != set(getattr(self, 'devices', [])):
                    self.after(0, self.refresh_devices)
            except Exception:
                pass
            time.sleep(3)

    def layout_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        header = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], height=60, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")

        title_text = f"AUTOPOST V{__version__}"
        ctk.CTkLabel(header, text=title_text, font=FONT_HEADER, text_color=COLORS["primary"]).pack(
            side="left", padx=25, pady=15)

        self.status_badge = ctk.CTkLabel(header, text="● IDLE", font=("Roboto", 13, "bold"),
                                         text_color=COLORS["text_sub"])
        self.status_badge.pack(side="right", padx=25)

        main_content = ctk.CTkFrame(self, fg_color="transparent")
        main_content.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        main_content.grid_rowconfigure(0, weight=1)
        main_content.grid_columnconfigure(0, weight=1)

        self.tabview = ctk.CTkTabview(main_content, fg_color=COLORS["bg_main"],
                                      segmented_button_fg_color=COLORS["bg_card"],
                                      segmented_button_selected_color=COLORS["primary"],
                                      segmented_button_unselected_color=COLORS["bg_card"],
                                      segmented_button_selected_hover_color=COLORS["primary"], corner_radius=12)
        self.tabview.grid(row=0, column=0, sticky="nsew")

        self.tab_dash = self.tabview.add("  Dashboard  ")
        self.tab_devices = self.tabview.add("  Devices  ")
        self.tab_config = self.tabview.add("  Settings  ")
        self.tab_logs = self.tabview.add("  System Logs  ")
        self.tab_adb = self.tabview.add("  ADB Utility  ")

        self.setup_dashboard()
        self.setup_devices()
        self.setup_config()
        self.setup_logs()
        self.setup_adb()

    def setup_dashboard(self):
        self.tab_dash.grid_columnconfigure(1, weight=1)
        self.tab_dash.grid_rowconfigure(0, weight=1)

        left_panel = ctk.CTkScrollableFrame(self.tab_dash, fg_color="transparent", width=360)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.overall_stats = StatsFrame(left_panel)
        self.overall_stats.pack(fill="x", pady=(0, 15))

        control_frame = ctk.CTkFrame(left_panel, fg_color=COLORS["bg_card"], corner_radius=15, border_width=1,
                                     border_color=COLORS["border"])
        control_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(control_frame, text="ACTIONS", font=("Roboto", 13, "bold"), text_color=COLORS["text_sub"]).pack(
            anchor="w", padx=20, pady=(15, 10))

        self.start_btn = ctk.CTkButton(control_frame, text="▶ START", height=45, fg_color=COLORS["success"],
                                       corner_radius=10,
                                       hover_color="#1E8233", font=("Roboto", 14, "bold"), command=self.start_threads)
        self.start_btn.pack(fill="x", padx=20, pady=(0, 10))

        self.stop_btn = ctk.CTkButton(control_frame, text="⏹ STOP PROCESS", height=45, fg_color=COLORS["danger"],
                                      corner_radius=10,
                                      hover_color="#C53030", font=("Roboto", 14, "bold"), state="disabled",
                                      command=self.stop_automation)
        self.stop_btn.pack(fill="x", padx=20, pady=(0, 10))

        # --- DELAY INPUTS ---
        lbl_delay = ctk.CTkLabel(control_frame, text="⚡ ACTION DELAY (Pre/Post)", font=("Roboto", 12, "bold"),
                                 text_color=COLORS["text_sub"])
        lbl_delay.pack(anchor="w", padx=20, pady=(10, 5))

        delay_row = ctk.CTkFrame(control_frame, fg_color="transparent")
        delay_row.pack(fill="x", padx=15, pady=(0, 10))

        self.dash_pre_delay = ctk.CTkEntry(delay_row, width=70, placeholder_text="Pre(s)", height=30, justify="center")
        self.dash_pre_delay.pack(side="left", padx=5)
        self.dash_pre_delay.insert(0, "10")

        ctk.CTkLabel(delay_row, text="/", font=("Roboto", 14)).pack(side="left")

        self.dash_post_delay = ctk.CTkEntry(delay_row, width=70, placeholder_text="Post(s)", height=30,
                                            justify="center")
        self.dash_post_delay.pack(side="left", padx=5)
        self.dash_post_delay.insert(0, "10")
        # ------------------------

        # BUTTONS
        unlock_btn = ctk.CTkButton(control_frame, text="🔓 UNLOCK (SWIPE UP)", height=35, fg_color=COLORS["primary"],
                                   corner_radius=10, hover_color="#3B82F6", font=("Roboto", 12, "bold"),
                                   command=self.action_go_home)
        unlock_btn.pack(fill="x", padx=20, pady=(0, 10))

        home_btn = ctk.CTkButton(control_frame, text="🏠 GO HOME", height=35, fg_color=COLORS["primary"],
                                 corner_radius=10, hover_color="#3B82F6", font=("Roboto", 12, "bold"),
                                 command=self.action_home_only)
        home_btn.pack(fill="x", padx=20, pady=(0, 10))

        awake_btn = ctk.CTkButton(control_frame, text="💡 KEEP SCREEN ON", height=35, fg_color="#8957e5",
                                  corner_radius=10, hover_color="#6e44b8", font=("Roboto", 12, "bold"),
                                  command=self.action_stay_awake)
        awake_btn.pack(fill="x", padx=20, pady=(0, 10))

        reset_btn = ctk.CTkButton(control_frame, text="⚡ FORCE RESET", height=35, fg_color=COLORS["warning"],
                                  corner_radius=10,
                                  hover_color="#B79034", text_color="#1A202C", font=("Roboto", 12, "bold"),
                                  command=self.system_full_reset)
        reset_btn.pack(fill="x", padx=20, pady=(0, 10))

        reboot_btn = ctk.CTkButton(control_frame, text="🔄 REBOOT ALL DEVICES", height=35, fg_color=COLORS["danger"],
                                   corner_radius=10,
                                   hover_color="#C53030", font=("Roboto", 12, "bold"),
                                   command=self.reboot_all_devices)
        reboot_btn.pack(fill="x", padx=20, pady=(0, 15))

        right_panel = ctk.CTkFrame(self.tab_dash, fg_color=COLORS["bg_card"], corner_radius=15, border_width=1,
                                   border_color=COLORS["border"])
        right_panel.grid(row=0, column=1, sticky="nsew")

        header = ctk.CTkFrame(right_panel, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=20)

        title_lbl = ctk.CTkLabel(header, text="🔗 LINK QUEUE", font=("Roboto", 18, "bold"),
                                 text_color=COLORS["primary"])
        title_lbl.pack(side="left")

        self.add_pair_btn = ctk.CTkButton(header, text="➕ ADD LINK", width=120, height=35, corner_radius=8,
                                          fg_color=COLORS["primary"], hover_color="#3B82F6",
                                          font=("Roboto", 13, "bold"), text_color="white", command=self.add_pair)
        self.add_pair_btn.pack(side="right")

        self.pairs_scroll = ctk.CTkScrollableFrame(right_panel, fg_color="transparent")
        self.pairs_scroll.pack(fill="both", expand=True, padx=15, pady=15)
        self.add_pair()

    def setup_devices(self):
        self.tab_devices.grid_columnconfigure(0, weight=1)
        self.tab_devices.grid_rowconfigure(1, weight=1)
        toolbar = ctk.CTkFrame(self.tab_devices, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        self.device_count_label = ctk.CTkLabel(toolbar, text="Connected: 0", font=FONT_SUBHEADER)
        self.device_count_label.pack(side="left", padx=10)
        refresh_btn = ctk.CTkButton(toolbar, text="🔄 Refresh List", width=130, height=35, corner_radius=8,
                                    font=("Roboto", 12, "bold"),
                                    fg_color=COLORS["bg_card"], border_width=1, border_color=COLORS["border"],
                                    command=self.refresh_devices)
        refresh_btn.pack(side="right", padx=10)
        self.device_config_frame = ctk.CTkScrollableFrame(self.tab_devices, fg_color=COLORS["bg_lighter"],
                                                          corner_radius=12)
        self.device_config_frame.grid(row=1, column=0, sticky="nsew")

    def setup_config(self):
        container = ctk.CTkFrame(self.tab_config, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        f1 = ctk.CTkFrame(container, fg_color=COLORS["bg_card"], corner_radius=15, border_width=1,
                          border_color=COLORS["border"])
        f1.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(f1, text="CORE SETTINGS", font=FONT_SUBHEADER, text_color=COLORS["primary"]).pack(anchor="w",
                                                                                                       padx=25,
                                                                                                       pady=(20, 15))
        f1_inner = ctk.CTkFrame(f1, fg_color="transparent")
        f1_inner.pack(fill="x", padx=25, pady=(0, 25))

        ctk.CTkLabel(f1_inner, text="Chrome Driver Path:", font=FONT_BODY).grid(row=0, column=0, sticky="w", pady=10)
        self.driver_entry = ctk.CTkEntry(f1_inner, width=450, height=40, corner_radius=8, fg_color=COLORS["bg_main"],
                                         border_color=COLORS["border"])
        self.driver_entry.grid(row=0, column=1, padx=15, pady=10)
        self.driver_entry.insert(0, self.chrome_driver_path)
        ctk.CTkButton(f1_inner, text="Browse", width=90, height=40, corner_radius=8, fg_color=COLORS["bg_lighter"],
                      border_width=1, border_color=COLORS["border"],
                      command=self.browse_driver).grid(row=0, column=2, padx=5)

        ctk.CTkLabel(f1_inner, text="Global Cookie File:", font=FONT_BODY).grid(row=1, column=0, sticky="w", pady=10)
        self.cookie_entry = ctk.CTkEntry(f1_inner, width=450, height=40, corner_radius=8, fg_color=COLORS["bg_main"],
                                         border_color=COLORS["border"])
        self.cookie_entry.grid(row=1, column=1, padx=15, pady=10)
        self.cookie_entry.insert(0, self.global_cookie_path)
        ctk.CTkButton(f1_inner, text="Browse", width=90, height=40, corner_radius=8, fg_color=COLORS["bg_lighter"],
                      border_width=1, border_color=COLORS["border"],
                      command=self.browse_global_cookie).grid(row=1, column=2, padx=5)

        f2 = ctk.CTkFrame(container, fg_color=COLORS["bg_card"], corner_radius=15, border_width=1,
                          border_color=COLORS["border"])
        f2.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(f2, text="TIMING & SAFETY", font=FONT_SUBHEADER, text_color=COLORS["primary"]).pack(anchor="w",
                                                                                                         padx=25,
                                                                                                         pady=(20, 15))
        f2_inner = ctk.CTkFrame(f2, fg_color="transparent")
        f2_inner.pack(fill="x", padx=25, pady=(0, 25))
        ctk.CTkLabel(f2_inner, text="Random Delay (Seconds):", font=FONT_BODY).grid(row=0, column=0, sticky="w",
                                                                                    pady=10)
        d_box = ctk.CTkFrame(f2_inner, fg_color="transparent")
        d_box.grid(row=0, column=1, sticky="w", padx=15)
        self.min_delay = ctk.CTkEntry(d_box, width=70, height=40, justify="center", corner_radius=8,
                                      fg_color=COLORS["bg_main"], border_color=COLORS["border"])
        self.min_delay.pack(side="left")
        self.min_delay.insert(0, "5")
        ctk.CTkLabel(d_box, text="  to  ", font=FONT_BODY).pack(side="left")
        self.max_delay = ctk.CTkEntry(d_box, width=70, height=40, justify="center", corner_radius=8,
                                      fg_color=COLORS["bg_main"], border_color=COLORS["border"])
        self.max_delay.pack(side="left")
        self.max_delay.insert(0, "10")

        ctk.CTkLabel(f2_inner, text="Max Retries:", font=FONT_BODY).grid(row=1, column=0, sticky="w", pady=10)
        self.retry_count = ctk.CTkEntry(f2_inner, width=70, height=40, justify="center", corner_radius=8,
                                        fg_color=COLORS["bg_main"], border_color=COLORS["border"])
        self.retry_count.grid(row=1, column=1, sticky="w", padx=15)
        self.retry_count.insert(0, "3")

        # INPUT FOR COOKIE LIMIT
        ctk.CTkLabel(f2_inner, text="Max Cookies per Device:", font=FONT_BODY).grid(row=2, column=0, sticky="w",
                                                                                    pady=10)
        self.cookie_limit_entry = ctk.CTkEntry(f2_inner, width=70, height=40, justify="center", corner_radius=8,
                                               fg_color=COLORS["bg_main"], border_color=COLORS["border"])
        self.cookie_limit_entry.grid(row=2, column=1, sticky="w", padx=15)
        self.cookie_limit_entry.insert(0, "0")

        ctk.CTkButton(container, text="💾 SAVE CONFIGURATION", height=50, width=250, font=("Roboto", 14, "bold"),
                      corner_radius=10,
                      fg_color=COLORS["primary"], command=self.save_config).pack(pady=15)

    def setup_logs(self):
        toolbar = ctk.CTkFrame(self.tab_logs, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, 15))

        self.filter_var = ctk.StringVar(value="All")
        ctk.CTkRadioButton(toolbar, text="All Logs", variable=self.filter_var, value="All", command=self.filter_logs,
                           font=FONT_BODY,
                           fg_color=COLORS["primary"]).pack(side="left", padx=15)
        ctk.CTkRadioButton(toolbar, text="Success Only", variable=self.filter_var, value="Success", font=FONT_BODY,
                           command=self.filter_logs, fg_color=COLORS["success"]).pack(side="left", padx=15)
        ctk.CTkRadioButton(toolbar, text="Errors Only", variable=self.filter_var, value="Error", font=FONT_BODY,
                           command=self.filter_logs, fg_color=COLORS["danger"]).pack(side="left", padx=15)

        ctk.CTkButton(toolbar, text="🗑 Clear", width=90, height=35, corner_radius=8, fg_color=COLORS["bg_card"],
                      font=("Roboto", 12, "bold"), border_width=1, border_color=COLORS["border"],
                      hover_color=COLORS["danger"], command=self.clear_logs).pack(side="right", padx=(5, 0))
        ctk.CTkButton(toolbar, text="📤 Export", width=90, height=35, corner_radius=8, fg_color=COLORS["bg_card"],
                      font=("Roboto", 12, "bold"), border_width=1, border_color=COLORS["border"],
                      hover_color=COLORS["primary"], command=self.export_logs).pack(side="right", padx=5)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                        background=COLORS["bg_card"],
                        foreground=COLORS["text_main"],
                        rowheight=40,
                        fieldbackground=COLORS["bg_card"],
                        bordercolor=COLORS["border"],
                        borderwidth=0,
                        font=("Roboto", 12))
        style.map('Treeview', background=[('selected', COLORS["primary"])])

        style.configure("Treeview.Heading",
                        background=COLORS["bg_lighter"],
                        foreground=COLORS["text_main"],
                        relief="flat",
                        font=("Roboto", 13, "bold"))
        style.map("Treeview.Heading", background=[('active', COLORS["bg_main"])])

        tree_frame = ctk.CTkFrame(self.tab_logs, corner_radius=0, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True)

        columns = ("Time", "Model", "Link", "Caption", "Status")
        self.log_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", style="Treeview")

        self.log_tree.heading("Time", text="TIME")
        self.log_tree.heading("Model", text="MODEL")
        self.log_tree.heading("Link", text="LINK")
        self.log_tree.heading("Caption", text="CAPTION")
        self.log_tree.heading("Status", text="STATUS")

        self.log_tree.column("Time", width=120, anchor="center")
        self.log_tree.column("Model", width=140, anchor="center")
        self.log_tree.column("Link", width=280, anchor="w")
        self.log_tree.column("Caption", width=280, anchor="w")
        self.log_tree.column("Status", width=160, anchor="center")

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.log_tree.yview)
        self.log_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.log_tree.pack(side="left", fill="both", expand=True)

        self.log_tree.tag_configure("SUCCESS", foreground=COLORS["success"])
        self.log_tree.tag_configure("ERROR", foreground=COLORS["danger"])
        self.log_tree.tag_configure("WARN", foreground=COLORS["warning"])
        self.log_tree.tag_configure("INFO", foreground="#4FC3F7")

        # --- ENABLE DOUBLE CLICK ---
        self.log_tree.bind("<Double-1>", self.on_log_double_click)

    def on_log_double_click(self, event):
        """Handle double clicks on log entries."""
        region = self.log_tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.log_tree.identify_column(event.x)
            if column == "#3":  # "Link" column
                item_id = self.log_tree.identify_row(event.y)
                item = self.log_tree.item(item_id)
                url = item['values'][2]
                if url and "http" in url:
                    try:
                        webbrowser.open(url)
                    except:
                        print(f"Error opening link: {e}")

    def setup_adb(self):
        container = ctk.CTkFrame(self.tab_adb, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        f1 = ctk.CTkFrame(container, fg_color=COLORS["bg_card"], corner_radius=15, border_width=1,
                          border_color=COLORS["border"])
        f1.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(f1, text="✈️ AIRPLANE MODE (ALL DEVICES)", font=FONT_SUBHEADER, text_color=COLORS["primary"]).pack(
            anchor="w", padx=25, pady=(20, 15))

        btn_frame1 = ctk.CTkFrame(f1, fg_color="transparent")
        btn_frame1.pack(fill="x", padx=25, pady=(0, 25))

        ctk.CTkButton(btn_frame1, text="Turn ON Airplane Mode", height=45, corner_radius=8, fg_color=COLORS["warning"],
                      hover_color="#B79034", text_color="#1A202C", font=("Roboto", 13, "bold"),
                      command=lambda: self.toggle_airplane_mode(True)).pack(side="left", padx=(0, 15))
        ctk.CTkButton(btn_frame1, text="Turn OFF Airplane Mode", height=45, corner_radius=8, fg_color=COLORS["success"],
                      hover_color="#1E8233", font=("Roboto", 13, "bold"),
                      command=lambda: self.toggle_airplane_mode(False)).pack(side="left")

        f2 = ctk.CTkFrame(container, fg_color=COLORS["bg_card"], corner_radius=15, border_width=1,
                          border_color=COLORS["border"])
        f2.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(f2, text="📦 BATCH APK INSTALLER", font=FONT_SUBHEADER, text_color=COLORS["primary"]).pack(
            anchor="w", padx=25, pady=(20, 15))

        f2_inner = ctk.CTkFrame(f2, fg_color="transparent")
        f2_inner.pack(fill="x", padx=25, pady=(0, 25))

        ctk.CTkLabel(f2_inner, text="APK File Path:", font=FONT_BODY).grid(row=0, column=0, sticky="w", pady=5)
        self.apk_entry = ctk.CTkEntry(f2_inner, width=450, height=40, corner_radius=8, fg_color=COLORS["bg_main"],
                                      border_color=COLORS["border"])
        self.apk_entry.grid(row=0, column=1, padx=15, pady=5)

        ctk.CTkButton(f2_inner, text="Browse", width=90, height=40, corner_radius=8, fg_color=COLORS["bg_lighter"],
                      border_width=1, border_color=COLORS["border"],
                      command=self.browse_apk).grid(row=0, column=2, padx=5)
        ctk.CTkButton(f2_inner, text="Install to All Devices", height=40, corner_radius=8, font=("Roboto", 13, "bold"),
                      fg_color=COLORS["primary"], command=self.install_apk_all).grid(row=0, column=3, padx=15)

        f3 = ctk.CTkFrame(container, fg_color=COLORS["bg_card"], corner_radius=15, border_width=1,
                          border_color=COLORS["border"])
        f3.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(f3, text="🛜 ADB WIRELESS (WIFI)", font=FONT_SUBHEADER, text_color=COLORS["primary"]).pack(
            anchor="w", padx=25, pady=(20, 15))

        btn_frame3 = ctk.CTkFrame(f3, fg_color="transparent")
        btn_frame3.pack(fill="x", padx=25, pady=(0, 25))

        ctk.CTkButton(btn_frame3, text="Turn ON Wireless ADB", height=45, corner_radius=8, fg_color=COLORS["success"],
                      hover_color="#1E8233", font=("Roboto", 13, "bold"), command=self.enable_wireless_adb).pack(
            side="left", padx=(0, 15))
        ctk.CTkButton(btn_frame3, text="Disconnect Wireless Devices", height=45, corner_radius=8,
                      fg_color=COLORS["warning"],
                      hover_color="#B79034", text_color="#1A202C", font=("Roboto", 13, "bold"),
                      command=self.disconnect_wireless_adb).pack(side="left")

    def toggle_airplane_mode(self, state):
        if not getattr(self, 'devices', []):
            messagebox.showwarning("Warning", "No devices connected!")
            return

        state_int = "1" if state else "0"
        state_bool = "true" if state else "false"
        CREATE_NO_WINDOW = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0

        def task():
            for dev in self.devices:
                subprocess.run(["adb", "-s", dev, "shell", "settings", "put", "global", "airplane_mode_on", state_int],
                               creationflags=CREATE_NO_WINDOW)
                subprocess.run(
                    ["adb", "-s", dev, "shell", "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE", "--ez",
                     "state", state_bool], creationflags=CREATE_NO_WINDOW)
                status_text = "ON" if state else "OFF"
                self.log_row(dev, "---", "---", f"AIRPLANE MODE {status_text}", "INFO")

            self.after(0, lambda: messagebox.showinfo("Success",
                                                      f"Airplane Mode turned {'ON' if state else 'OFF'} for all devices."))

        threading.Thread(target=task, daemon=True).start()

    def browse_apk(self):
        file = filedialog.askopenfilename(filetypes=[("APK files", "*.apk")])
        if file:
            self.apk_entry.delete(0, "end")
            self.apk_entry.insert(0, file)

    def install_apk_all(self):
        apk_path = self.apk_entry.get().strip()
        if not apk_path or not os.path.exists(apk_path):
            messagebox.showerror("Error", "Please select a valid APK file.")
            return

        if not getattr(self, 'devices', []):
            messagebox.showwarning("Warning", "No devices connected!")
            return

        CREATE_NO_WINDOW = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0

        def task():
            for dev in self.devices:
                self.log_row(dev, "---", "---", "INSTALLING APK...", "INFO")
                try:
                    res = subprocess.run(["adb", "-s", dev, "install", "-r", apk_path], capture_output=True, text=True,
                                         creationflags=CREATE_NO_WINDOW)
                    if "Success" in res.stdout:
                        self.log_row(dev, "---", "---", "APK INSTALLED", "SUCCESS")
                    else:
                        self.log_row(dev, "---", "---", "APK INSTALL FAILED", "ERROR")
                except:
                    self.log_row(dev, "---", "---", f"INSTALL ERROR", "ERROR")

            self.after(0,
                       lambda: messagebox.showinfo("Done", "Batch APK installation completed. Check logs for details."))

        threading.Thread(target=task, daemon=True).start()

    def reboot_all_devices(self):
        if not getattr(self, 'devices', []):
            messagebox.showwarning("Warning", "No devices connected!")
            return

        confirm = messagebox.askyesno("Confirm Reboot", "Are you sure you want to reboot ALL connected devices?")
        if not confirm:
            return

        CREATE_NO_WINDOW = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0

        def task():
            for dev in self.devices:
                self.log_row(dev, "---", "---", "REBOOTING DEVICE...", "WARN")
                try:
                    subprocess.Popen(["adb", "-s", dev, "reboot"], creationflags=CREATE_NO_WINDOW)
                except:
                    self.log_row(dev, "---", "---", f"REBOOT ERROR", "ERROR")

            self.after(0, lambda: messagebox.showinfo("Done",
                                                      "Reboot command sent to all devices. They will disconnect momentarily."))

        threading.Thread(target=task, daemon=True).start()

    def action_go_home(self):
        if not getattr(self, 'devices', []):
            messagebox.showwarning("Warning", "No devices connected!")
            return

        CREATE_NO_WINDOW = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0

        def task():
            for dev in self.devices:
                self.log_row(dev, "---", "---", "SWIPING UP TO UNLOCK...", "INFO")
                try:
                    # 1. Wake screen (224)
                    subprocess.run(["adb", "-s", dev, "shell", "input", "keyevent", "224"],
                                   creationflags=CREATE_NO_WINDOW)
                    time.sleep(0.5)

                    # 2. Swipe Up (200 500 -> 200 0)
                    subprocess.run(["adb", "-s", dev, "shell", "input", "swipe", "200", "500", "200", "0", "300"],
                                   creationflags=CREATE_NO_WINDOW)
                    time.sleep(1)

                    # 3. Press Home (3) just in case
                    subprocess.run(["adb", "-s", dev, "shell", "input", "keyevent", "3"],
                                   creationflags=CREATE_NO_WINDOW)

                    self.log_row(dev, "---", "---", "DEVICE UNLOCKED/HOME", "SUCCESS")
                except:
                    self.log_row(dev, "---", "---", "UNLOCK FAILED", "ERROR")

            self.after(0, lambda: messagebox.showinfo("Done", "Unlock command sent to all devices."))

        threading.Thread(target=task, daemon=True).start()

    def action_home_only(self):
        if not getattr(self, 'devices', []):
            messagebox.showwarning("Warning", "No devices connected!")
            return

        CREATE_NO_WINDOW = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0

        def task():
            for dev in self.devices:
                self.log_row(dev, "---", "---", "GOING HOME...", "INFO")
                try:
                    # Just keyevent 3
                    subprocess.run(["adb", "-s", dev, "shell", "input", "keyevent", "3"],
                                   creationflags=CREATE_NO_WINDOW)
                    self.log_row(dev, "---", "---", "DEVICE AT HOME", "SUCCESS")
                except:
                    self.log_row(dev, "---", "---", "HOME FAILED", "ERROR")

            self.after(0, lambda: messagebox.showinfo("Done", "Home command sent to all devices."))

        threading.Thread(target=task, daemon=True).start()

    def action_stay_awake(self):
        if not getattr(self, 'devices', []):
            messagebox.showwarning("Warning", "No devices connected!")
            return

        CREATE_NO_WINDOW = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0

        def task():
            for dev in self.devices:
                self.log_row(dev, "---", "---", "SETTING ALWAYS ON...", "INFO")
                try:
                    # svc power stayon true (Keeps screen on when plugged into USB)
                    subprocess.run(["adb", "-s", dev, "shell", "svc", "power", "stayon", "true"],
                                   creationflags=CREATE_NO_WINDOW)
                    # Also wake it up now just in case
                    subprocess.run(["adb", "-s", dev, "shell", "input", "keyevent", "224"],
                                   creationflags=CREATE_NO_WINDOW)
                    self.log_row(dev, "---", "---", "SCREEN SET TO AWAKE", "SUCCESS")
                except:
                    self.log_row(dev, "---", "---", "SET AWAKE FAILED", "ERROR")

            self.after(0, lambda: messagebox.showinfo("Done", "Devices set to Stay Awake (while charging)."))

        threading.Thread(target=task, daemon=True).start()

    def enable_wireless_adb(self):
        if not getattr(self, 'devices', []):
            messagebox.showwarning("Warning", "No devices connected!")
            return

        CREATE_NO_WINDOW = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0

        def task():
            for dev in self.devices:
                if ":" in dev or "." in dev:
                    continue

                self.log_row(dev, "---", "---", "ENABLING WIRELESS ADB...", "INFO")
                try:
                    subprocess.run(["adb", "-s", dev, "tcpip", "5555"], capture_output=True,
                                   creationflags=CREATE_NO_WINDOW)
                    time.sleep(2)

                    ip_out = subprocess.check_output(["adb", "-s", dev, "shell", "ip", "route"],
                                                     creationflags=CREATE_NO_WINDOW).decode('utf-8')
                    ip = None
                    for line in ip_out.split('\n'):
                        if 'src' in line and ('wlan' in line or 'rmnet' in line):
                            parts = line.split()
                            if 'src' in parts:
                                ip = parts[parts.index('src') + 1]
                                break

                    if not ip:
                        ip_out2 = subprocess.check_output(["adb", "-s", dev, "shell", "ip", "addr", "show", "wlan0"],
                                                          creationflags=CREATE_NO_WINDOW).decode('utf-8')
                        for line in ip_out2.split('\n'):
                            if 'inet ' in line:
                                ip = line.strip().split()[1].split('/')[0]
                                break

                    if ip:
                        res = subprocess.run(["adb", "connect", f"{ip}:5555"], capture_output=True, text=True,
                                             creationflags=CREATE_NO_WINDOW)
                        if "connected" in res.stdout.lower():
                            self.log_row(dev, "---", "---", f"WIRELESS CONNECTED ({ip})", "SUCCESS")
                        else:
                            self.log_row(dev, "---", "---", f"WIRELESS FAILED ({ip})", "ERROR")
                    else:
                        self.log_row(dev, "---", "---", "NO WIFI IP FOUND", "ERROR")

                except:
                    self.log_row(dev, "---", "---", f"WIFI ERROR: {e}", "ERROR")

            self.after(0, lambda: messagebox.showinfo("Done",
                                                      "Wireless setup complete. You may now unplug USB cables if connected successfully."))
            self.after(2000, self.refresh_devices)

        threading.Thread(target=task, daemon=True).start()

    def disconnect_wireless_adb(self):
        CREATE_NO_WINDOW = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0

        def task():
            subprocess.run(["adb", "disconnect"], creationflags=CREATE_NO_WINDOW)
            self.after(0, lambda: messagebox.showinfo("Done", "Disconnected all wireless devices."))
            self.after(1000, self.refresh_devices)

        threading.Thread(target=task, daemon=True).start()

    def add_pair(self):
        pair_num = len(self.pair_widgets) + 1
        new_pair = PairFrame(self.pairs_scroll, pair_num, lambda: self.remove_pair(new_pair))
        new_pair.pack(fill="x", padx=5, pady=10)
        self.pair_widgets.append(new_pair)

    def remove_pair(self, frame_to_remove):
        if len(self.pair_widgets) > 1:
            frame_to_remove.destroy()
            self.pair_widgets.remove(frame_to_remove)
            for i, frame in enumerate(self.pair_widgets):
                frame.header_label.configure(text=f"📍 TASK #{i + 1}")

    def browse_driver(self):
        file = filedialog.askopenfilename(filetypes=[("Executable files", "*.exe")])
        if file:
            self.driver_entry.delete(0, "end")
            self.driver_entry.insert(0, file)
            self.chrome_driver_path = file

    def browse_global_cookie(self):
        file = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file:
            self.cookie_entry.delete(0, "end")
            self.cookie_entry.insert(0, file)
            self.global_cookie_path = file

    def save_config(self):
        self.chrome_driver_path = self.driver_entry.get()
        self.global_cookie_path = self.cookie_entry.get()
        self.saved_settings["cookie_limit"] = self.cookie_limit_entry.get()
        # SAVE DASHBOARD DELAY SETTINGS
        if hasattr(self, 'dash_pre_delay'):
            self.saved_settings["dash_pre_delay"] = self.dash_pre_delay.get()
            self.saved_settings["dash_post_delay"] = self.dash_post_delay.get()

        self.save_settings()
        messagebox.showinfo("Saved", "Configuration updated successfully.")

    def filter_logs(self):
        filter_value = self.filter_var.get()
        for item in self.log_tree.get_children():
            self.log_tree.delete(item)

        for log_entry in self.all_logs:
            if filter_value == "All" or filter_value.lower() in log_entry["status"].lower() or filter_value.upper() == \
                    log_entry["level"]:
                self.display_log_entry(log_entry)

    def export_logs(self):
        file = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file:
            with open(file, "w") as f:
                f.write(f"{'TIME':<12} | {'DEVICE':<10} | {'LINK':<40} | {'CAPTION':<40} | {'STATUS'}\n")
                f.write("-" * 120 + "\n")
                for log_entry in self.all_logs:
                    f.write(
                        f"{log_entry['timestamp']:<12} | {log_entry['device']:<10} | {log_entry['link']:<40} | {log_entry['caption']:<40} | {log_entry['status']}\n")
            messagebox.showinfo("Exported", f"Logs saved to {file}")

    def clear_logs(self):
        for item in self.log_tree.get_children():
            self.log_tree.delete(item)
        self.all_logs = []

    def get_manila_time(self):
        # CHANGED TO 12-HOUR AM/PM FORMAT
        return datetime.now().strftime("%I:%M:%S %p")

    def load_settings(self):
        settings_file = "device_settings.json"
        if os.path.exists(settings_file):
            try:
                with open(settings_file, "r") as f:
                    data = json.load(f)
                    self.chrome_driver_path = data.get("chrome_driver_path", "chromedriver.exe")
                    self.global_cookie_path = data.get("global_cookie_path", "")

                    limit = data.get("cookie_limit", "0")
                    # DEFAULT TO 10
                    pre_d = data.get("dash_pre_delay", "10")
                    post_d = data.get("dash_post_delay", "10")

                    self.after(500, lambda: self.set_ui_values(limit, pre_d, post_d))
                    return data
            except:
                return {}
        return {}

    def set_ui_values(self, limit, pre, post):
        if hasattr(self, 'cookie_limit_entry'):
            self.cookie_limit_entry.delete(0, "end")
            self.cookie_limit_entry.insert(0, str(limit))
        if hasattr(self, 'dash_pre_delay'):
            self.dash_pre_delay.delete(0, "end")
            self.dash_pre_delay.insert(0, str(pre))
        if hasattr(self, 'dash_post_delay'):
            self.dash_post_delay.delete(0, "end")
            self.dash_post_delay.insert(0, str(post))

    def save_settings(self):
        settings_file = "device_settings.json"
        self.saved_settings["chrome_driver_path"] = self.chrome_driver_path
        self.saved_settings["global_cookie_path"] = self.global_cookie_path
        try:
            with open(settings_file, "w") as f:
                json.dump(self.saved_settings, f, indent=2)
        except:
            pass

    def system_full_reset(self):
        self.log_row("SYSTEM", "---", "---", "INITIATING RESET...", "WARN")
        try:
            if os.name == 'nt':
                subprocess.run(["taskkill", "/F", "/IM", "chromedriver.exe", "/T"], capture_output=True,
                               creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                subprocess.run(["pkill", "chromedriver"], capture_output=True)
            if self.devices:
                for d in self.devices:
                    subprocess.run(["adb", "-s", d, "shell", "pm", "clear", "com.android.chrome"], capture_output=True,
                                   creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            subprocess.run(["adb", "kill-server"], capture_output=True,
                           creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            time.sleep(1)
            subprocess.run(["adb", "start-server"], capture_output=True,
                           creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            self.log_row("SYSTEM", "---", "---", "FULL WIPE COMPLETE", "SUCCESS")
            self.refresh_devices()
        except:
            self.log_row("SYSTEM", "---", "---", "RESET ERROR", "ERROR")

    def log_row(self, device, link, caption, status, level="INFO"):
        timestamp = self.get_manila_time()
        d_name = device[:8] if device else "SYSTEM"
        if "SUCCESS" in status.upper():
            level = "SUCCESS"
        elif "FAIL" in status.upper() or "ERROR" in status.upper():
            level = "ERROR"

        log_entry = {
            "timestamp": timestamp,
            "device": d_name,
            "link": link,
            "caption": caption,
            "status": status,
            "level": level
        }
        self.all_logs.append(log_entry)

        self.after(0, lambda e=log_entry: self.display_log_entry(e))

    def display_log_entry(self, log_entry):
        ts = log_entry["timestamp"]
        dev = log_entry["device"]
        link = log_entry["link"]
        cap = log_entry["caption"]
        status = log_entry["status"]
        level = log_entry["level"]

        disp_link = (link[:47] + '...') if len(link) > 50 else link
        disp_cap = (cap[:47] + '...') if len(cap) > 50 else cap

        item = self.log_tree.insert("", "end", values=(ts, dev, disp_link, disp_cap, status), tags=(level,))
        self.log_tree.see(item)

    def refresh_devices(self):
        try:
            CREATE_NO_WINDOW = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            o = subprocess.check_output(["adb", "devices"], creationflags=CREATE_NO_WINDOW).decode("utf-8")
            current_devices = [l.split()[0] for l in o.strip().split("\n")[1:] if
                               "device" in l and not l.startswith("*")]
            self.devices = current_devices

            self.device_count_label.configure(text=f"Connected: {len(self.devices)}")

            self.overall_stats.update_devices(len(self.devices))

            for widget in self.device_config_frame.winfo_children():
                widget.destroy()
            self.device_widgets = []

            if not self.devices:
                ctk.CTkLabel(self.device_config_frame, text="No Android devices found via ADB.", text_color="#666",
                             font=FONT_BODY).pack(pady=20)
                return

            for device in self.devices:
                device_frame = DeviceFrame(self.device_config_frame, device)
                device_frame.pack(fill="x", padx=15, pady=8)
                self.device_widgets.append(device_frame)
                threading.Thread(target=self.get_device_info, args=(device, device_frame), daemon=True).start()

        except:
            self.device_count_label.configure(text="Devices: ADB Error")

    def get_device_info(self, device_id, device_frame):
        try:
            CREATE_NO_WINDOW = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            model_result = subprocess.run(["adb", "-s", device_id, "shell", "getprop", "ro.product.model"],
                                          capture_output=True, text=True, creationflags=CREATE_NO_WINDOW).stdout.strip()
            version_result = subprocess.run(["adb", "-s", device_id, "shell", "getprop", "ro.build.version.release"],
                                            capture_output=True, text=True,
                                            creationflags=CREATE_NO_WINDOW).stdout.strip()

            res_output = subprocess.run(["adb", "-s", device_id, "shell", "wm", "size"],
                                        capture_output=True, text=True, creationflags=CREATE_NO_WINDOW).stdout.strip()
            if "size:" in res_output:
                dims = res_output.split()[-1].split("x")
                self.device_resolutions[device_id] = (int(dims[0]), int(dims[1]))

            self.after(100, lambda: device_frame.update_device_info(model_result, version_result))
        except:
            self.device_resolutions[device_id] = (1080, 2400)

    def parse_cookies(self, cookie_str):
        cookies = []
        for pair in cookie_str.split(";"):
            if "=" in pair:
                name, value = pair.strip().split("=", 1)
                cookies.append({"name": name, "value": value, "domain": ".facebook.com"})
        return cookies

    def run_fb_automation(self, device_id, job_list, device_cookies, start_index):
        global post_box
        options = Options()
        options.add_experimental_option("androidPackage", "com.android.chrome")
        options.add_experimental_option("androidDeviceSerial", device_id)
        options.add_argument("--blink-settings=imagesEnabled=false,videoAutoplayEnabled=false")
        options.add_argument("--disable-notifications")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_argument("--no-sandbox")
        options.add_argument("--mute-audio")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-fre")
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--disable-popup-blocking")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])

        service = Service(executable_path=self.chrome_driver_path)
        local_cookies = list(device_cookies)

        # --- GET DELAY SETTINGS ---
        try:
            pre_wait = float(self.dash_pre_delay.get())
        except:
            pre_wait = 10  # Default fallback
        try:
            post_wait = float(self.dash_post_delay.get())
        except:
            post_wait = 10  # Default fallback
        # --------------------------

        cookie_counter = 0

        while local_cookies and self.is_running:
            cookie_str = local_cookies.pop(0)

            # --- ACCOUNT NUMBER TRACKING ---
            current_account_num = start_index + cookie_counter
            cookie_counter += 1

            driver = None
            CREATE_NO_WINDOW = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0

            try:
                subprocess.run(["adb", "-s", device_id, "shell", "pm", "clear", "com.android.chrome"],
                               capture_output=True, creationflags=CREATE_NO_WINDOW)
                time.sleep(3)
                driver = webdriver.Chrome(service=service, options=options)
                wait = WebDriverWait(driver, 10)
                driver.get("https://m.facebook.com")

                for c in self.parse_cookies(cookie_str):
                    try:
                        driver.add_cookie(c)
                    except:
                        continue
                time.sleep(5)
                driver.refresh()
                time.sleep(5)

                if "login" in driver.current_url.lower() or "checkpoint" in driver.current_url.lower():
                    raise Exception("Account Error - Na-checkpoint o hindi naka-log in.")
                time.sleep(6)

                # --- ENUMERATE FOR LINK NUMBER TRACKING ---
                for link_num, (link, caption_file) in enumerate(job_list, 1):
                    if not self.is_running: break
                    sel_cap = "---"

                    # --- RETRY LOGIC FOR COMPOSER / SEND KEYS ---
                    max_composer_retries = 3
                    post_success = False

                    for attempt in range(max_composer_retries):
                        if not self.is_running: break
                        try:
                            # 1. Navigate/Refresh Composer
                            driver.get("https://m.facebook.com/composer/")

                            # 2. Find Trigger/Box
                            try:
                                trigger_xpath = "//div[@data-mcomponent='TextArea'] | //div[@aria-label=\"What's on your mind?\"] | //div[@role='button' and .//span[text()=\"What's on your mind?\"]]"
                                trigger_btn = WebDriverWait(driver, 5).until(
                                    EC.element_to_be_clickable((By.XPATH, trigger_xpath)))
                                time.sleep(pre_wait)
                                trigger_btn.click()
                                time.sleep(post_wait)
                            except:
                                try:
                                    trigger_xpath = "//div[contains(@aria-label, 'mind')]"
                                    trigger = WebDriverWait(driver, 5).until(
                                        EC.element_to_be_clickable((By.XPATH, trigger_xpath)))
                                    time.sleep(pre_wait)
                                    trigger.click()
                                    time.sleep(post_wait)
                                except:
                                    pass

                            post_box = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
                                (By.XPATH, "//div[@role='textbox' and @contenteditable='true'] | //textarea")
                            ))

                            time.sleep(pre_wait)
                            post_box.click()
                            time.sleep(post_wait)

                            # 3. Input Link
                            if link and link.strip():
                                time.sleep(2)
                                time.sleep(pre_wait)
                                post_box.send_keys(link)
                                time.sleep(post_wait)

                                time.sleep(6)
                                driver.execute_script("document.activeElement.blur()")
                                time.sleep(2)

                                # Re-focus attempts
                                try:
                                    trigger = wait.until(EC.element_to_be_clickable((By.XPATH,
                                                                                     "//div[contains(@aria-label, 'mind')] | //textarea | //div[@role='textbox']")))
                                    time.sleep(pre_wait)
                                    trigger.click()
                                    time.sleep(post_wait)
                                    time.sleep(6)
                                except:
                                    pass

                                while True:
                                    try:
                                        time.sleep(pre_wait)
                                        post_box.send_keys(Keys.CONTROL, "a")
                                        time.sleep(post_wait)
                                        time.sleep(pre_wait)
                                        post_box.send_keys(Keys.BACK_SPACE)
                                        time.sleep(post_wait)
                                        driver.execute_script("document.activeElement.blur()")
                                        time.sleep(pre_wait)
                                        break
                                    except:
                                        pass

                            if caption_file and os.path.exists(caption_file):
                                with open(caption_file, "r", encoding="utf-8") as f:
                                    caps = [line.strip() for line in f if line.strip()]
                                if caps:
                                    sel_cap = random.choice(caps)
                                    time.sleep(pre_wait)
                                    post_box.send_keys(sel_cap)
                                    time.sleep(post_wait)
                                    time.sleep(2)

                            # 5. Click Post
                            post_xpath = "//button[@name='view_post'] | //button[@value='Post'] | //input[@value='Post'] | //div[translate(@aria-label, 'POST', 'post')='post'] | //span[translate(text(), 'POST', 'post')='post']"
                            post_btn = wait.until(EC.presence_of_element_located((By.XPATH, post_xpath)))
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", post_btn)
                            time.sleep(6)

                            time.sleep(pre_wait)
                            driver.execute_script("arguments[0].click();", post_btn)
                            time.sleep(post_wait)

                            time.sleep(6)

                            # --- SUCCESS LOG WITH NUMBERS ---
                            status_msg = f"SUCCESS [L#{link_num}][Acc#{current_account_num}]"
                            self.log_row(device_id, link if link else "---", sel_cap, status_msg, "SUCCESS")

                            self.total_shares += 1
                            self.total_attempts += 1
                            self.update_stats()

                            post_success = True
                            break

                        except:
                            self.log_row(device_id, link, "---", f"RETRYING POST ({attempt + 1}/3)...", "WARN")
                            time.sleep(2)
                            continue

                    if not post_success:
                        self.log_row(device_id, link, "---", f"SKIP [L#{link_num}] (MAX RETRIES)", "ERROR")
                        self.total_attempts += 1
                        self.update_stats()

                    # Random Delay between posts
                    try:
                        delay = random.randint(int(self.min_delay.get() or 5), int(self.max_delay.get() or 10))
                    except:
                        delay = random.randint(5, 10)
                    time.sleep(delay)

                driver.quit()

            except:
                # --- ACCOUNT FAILED LOGIC WITH NUMBER ---
                self.log_row(device_id, "---", "---", f"ACCOUNT #{current_account_num} FAILED", "ERROR")
                self.error_count += 1
                self.total_attempts += 1
                self.update_stats()

                if driver:
                    try:
                        driver.quit()
                    except:
                        pass

                # --- AUTO REBOOT DEVICE ---
                self.log_row(device_id, "---", "---", "REBOOTING DEVICE (FAIL RECOVERY)...", "WARN")
                try:
                    subprocess.run(["adb", "-s", device_id, "reboot"], creationflags=CREATE_NO_WINDOW)
                    # WAIT FOR BOOTUP (60 SECONDS)
                    for i in range(60):
                        if not self.is_running: break
                        time.sleep(1)
                    self.log_row(device_id, "---", "---", "DEVICE REBOOT WAIT DONE", "INFO")
                except:
                    self.log_row(device_id, "---", "---", "REBOOT FAILED", "ERROR")

    def update_stats(self):
        self.after(0, lambda: self.overall_stats.update_stats(self.total_shares, self.error_count))

    def start_threads(self):
        if not self.devices:
            messagebox.showerror("Error", "No devices connected!")
            return

        jobs = [(p.link_entry.get(), p.caption_path.get()) for p in self.pair_widgets if
                p.link_entry.get().strip() or p.caption_path.get().strip()]

        if not jobs:
            messagebox.showerror("Error", "No links/jobs configured!")
            return

        cookie_file = self.cookie_entry.get().strip()
        if not cookie_file or not os.path.exists(cookie_file):
            messagebox.showerror("Error", "Please select a valid Global Cookie File in Settings!")
            return

        try:
            with open(cookie_file, "r") as f:
                all_cookies = [line.strip() for line in f if line.strip()]
        except:
            messagebox.showerror("Error", f"Failed to read cookie file: {e}")
            return

        if not all_cookies:
            messagebox.showerror("Error", "The cookie file is empty!")
            return

        device_jobs = []
        total_devices = len(self.devices)

        # COOKIE LIMIT LOGIC
        try:
            limit_per_dev = int(self.cookie_limit_entry.get())
        except:
            limit_per_dev = 0

        if limit_per_dev > 0:
            cursor = 0
            for device in self.devices:
                if cursor >= len(all_cookies):
                    break

                end_idx = cursor + limit_per_dev
                if end_idx > len(all_cookies):
                    end_idx = len(all_cookies)

                chunk = all_cookies[cursor:end_idx]
                if chunk:
                    # PASS START INDEX (cursor + 1 for human readable)
                    device_jobs.append((device, chunk, cursor + 1))

                cursor += limit_per_dev
        else:
            for i, device in enumerate(self.devices):
                start_idx = i * len(all_cookies) // total_devices
                end_idx = (i + 1) * len(all_cookies) // total_devices
                device_cookies = all_cookies[start_idx:end_idx]

                if device_cookies:
                    # PASS START INDEX
                    device_jobs.append((device, device_cookies, start_idx + 1))

        if not device_jobs:
            messagebox.showerror("Error", "Not enough cookies to distribute or limit is too strict!")
            return

        self.is_running = True
        self.start_time = datetime.now()
        self.status_badge.configure(text="● RUNNING", text_color=COLORS["success"])
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")

        def manager():
            threads = []
            for device_id, cookie_list, start_idx in device_jobs:
                t = threading.Thread(target=self.run_fb_automation, args=(device_id, jobs, cookie_list, start_idx))
                t.start()
                threads.append(t)
            for t in threads: t.join()
            self.is_running = False

            self.after(0, self._reset_ui_after_run)

        threading.Thread(target=manager, daemon=True).start()

    def _reset_ui_after_run(self):
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.status_badge.configure(text="● IDLE", text_color=COLORS["text_sub"])

    def stop_automation(self):
        self.is_running = False
        self.stop_btn.configure(state="disabled")
        self.status_badge.configure(text="● STOPPING...", text_color=COLORS["warning"])

    def on_close(self):
        self.destroy()
        os._exit(0)


if __name__ == "__main__":
    app = FacebookAutomationGUI()
    app.mainloop()
