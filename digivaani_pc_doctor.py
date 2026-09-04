#!/usr/bin/env python3
"""
DigiVaani PC Doctor - GUI Version
Version : 1.0
Brand   : DigiVaani"
Author  : 64yadav
WEBSITE = "https://digivaani64-hub.github.io/digivaani/"
GITHUB = "https://github.com/digivaani64-hub/digivaani"
TELEGRAM = "https://t.me/DigiVaani"  

"""

import ctypes
import datetime
import json
import os
import subprocess
import sys
import tempfile
import threading
import webbrowser
from pathlib import Path

import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

IS_WINDOWS = os.name == "nt"
if IS_WINDOWS:
    import winreg
    CREATE_NO_WINDOW = subprocess.CREATE_NO_WINDOW
else:
    CREATE_NO_WINDOW = 0

# ==================== BRANDING ====================
APP_NAME = "PC Doctor by DigiVaani"
VERSION = "1.0"
CREATOR = "64 Yadav"
WEBSITE = "https://digivaani64-hub.github.io/digivaani/"
GITHUB = "https://github.com/digivaani64-hub/digivaani"
TELEGRAM = "https://t.me/DigiVaani"  

BASE_DIR = Path(sys.executable).parent if getattr(sys, "frozen", False) \
    else Path(__file__).resolve().parent
LOG_TXT = BASE_DIR / "DigiVaani_PC_Doctor_log.txt"
LOG_JSON = BASE_DIR / "digivaani_pcdoctor_actions.json"
BACKUP_DIR = BASE_DIR / "digivaani_backup"

# ==================== THEME ====================
BG = "#1e1e2e"
BG_DARK = "#11111b"
CARD = "#313244"
CARD_HOVER = "#45475a"
FG = "#cdd6f4"
FG_MUTED = "#a6adc8"
ACCENT = "#cba6f7"
GREEN = "#a6e3a1"
RED = "#f38ba8"
YELLOW = "#f9e2af"

# ==================== CURATED SAFETY LISTS ====================
# Conservative substrings for common OEM / low-value Store apps.
BLOATWARE_FRAGMENTS = [
    "Microsoft.BingWeather", "Microsoft.BingNews", "Microsoft.BingFinance",
    "Microsoft.BingSports", "Microsoft.GetHelp", "Microsoft.Getstarted",
    "Microsoft.Messaging", "Microsoft.Microsoft3DViewer",
    "Microsoft.MicrosoftSolitaireCollection", "Microsoft.MixedReality.Portal",
    "Microsoft.OneConnect", "Microsoft.People", "Microsoft.Print3D",
    "Microsoft.SkypeApp", "Microsoft.WindowsAlarms",
    "Microsoft.WindowsFeedbackHub", "Microsoft.WindowsMaps",
    "Microsoft.WindowsSoundRecorder", "Microsoft.Xbox", "Microsoft.YourPhone",
    "Microsoft.ZuneMusic", "Microsoft.ZuneVideo", "Clipchamp.Clipchamp",
    "king.com", "Facebook", "Spotify", "Disney", "TikTok", "Netflix",
]
# Safety net -- never offered for removal even if a fragment above matches.
BLOATWARE_NEVER_TOUCH = [
    "Microsoft.WindowsStore", "Microsoft.SecHealthUI",
    "Microsoft.Windows.Photos", "Microsoft.WindowsCalculator",
    "Microsoft.WindowsCamera", "Microsoft.WindowsNotepad",
    "Microsoft.DesktopAppInstaller", "Microsoft.VCLibs",
    "Microsoft.NET.Native", "Microsoft.UI.Xaml",
]
# (service_name, human reason) -- conservative, well-known safe-to-disable set.
SAFE_SERVICES = [
    ("Fax", "Fax service -- unused on almost every modern PC"),
    ("RemoteRegistry", "Remote registry editing -- security risk if unused"),
    ("PrintNotify", "Printer notifications -- only needed if printing"),
    ("WSearch", "Windows Search indexing -- heavy on old/slow disks"),
    ("SysMain", "Superfetch -- can help SSDs, often unhelpful on old HDDs"),
    ("DiagTrack", "Connected User Experiences & Telemetry"),
    ("MapsBroker", "Downloaded Maps Manager -- unused unless offline Maps"),
    ("RetailDemo", "Retail Demo Service -- only for in-store display PCs"),
]

DEFENDER_PATHS = [
    r"C:\Program Files\Windows Defender\MpCmdRun.exe",
    os.path.expandvars(r"%ProgramFiles%\Windows Defender\MpCmdRun.exe"),
]


# ==================== UTILITIES ====================
def human_size(num_bytes):
    n = float(num_bytes)
    for unit in ["B", "KB", "MB", "GB"]:
        if n < 1024:
            return f"{n:.2f} {unit}"
        n /= 1024
    return f"{n:.2f} TB"


def get_folder_size(path):
    total = 0
    try:
        for entry in Path(path).rglob("*"):
            try:
                if entry.is_file():
                    total += entry.stat().st_size
            except OSError:
                continue
    except OSError:
        pass
    return total


def is_admin():
    if not IS_WINDOWS:
        return False
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def relaunch_as_admin():
    try:
        if getattr(sys, "frozen", False):
            target, params = sys.executable, ""
        else:
            target, params = sys.executable, f'"{os.path.abspath(__file__)}"'
        ctypes.windll.shell32.ShellExecuteW(None, "runas", target, params, None, 1)
        return True
    except Exception:
        return False


def log_text(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(LOG_TXT, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    except OSError:
        pass


def load_actions():
    if not LOG_JSON.exists():
        return []
    try:
        return json.loads(LOG_JSON.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def save_actions(entries):
    try:
        LOG_JSON.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass


def log_action(module, action, details, undo=None):
    entries = load_actions()
    entries.append({
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        "module": module, "action": action, "details": details, "undo": undo,
    })
    save_actions(entries)


def run_capture(args, timeout=None):
    """Run a command, capture output, never raise. Returns (rc, stdout, stderr)."""
    try:
        result = subprocess.run(
            args, capture_output=True, text=True, encoding="utf-8", errors="ignore",
            timeout=timeout, creationflags=CREATE_NO_WINDOW,
        )
        return result.returncode, result.stdout, result.stderr
    except FileNotFoundError:
        return -1, "", f"Command not found: {args[0]}"
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)


def run_powershell(script, timeout=None):
    return run_capture(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
        timeout=timeout,
    )


def find_mpcmdrun():
    for path in DEFENDER_PATHS:
        if os.path.isfile(path):
            return path
    return None


# ==================== MAIN APP ====================
class DigiVaaniApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} v{VERSION}")
        self.root.geometry("820x680")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        self.busy = False
        self.action_buttons = []
        self.build_ui()
        self.write_log(f"Welcome to {APP_NAME} v{VERSION}. Ready.")
        if not is_admin():
            self.write_log("Not running as Administrator -- some actions "
                            "(services, DISM, some registry edits) may fail.")

    # ---------- UI construction ----------
    def build_ui(self):
        header = tk.Frame(self.root, bg=BG_DARK, height=90)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text=APP_NAME, font=("Segoe UI", 20, "bold"),
                 fg=ACCENT, bg=BG_DARK).pack(pady=(15, 0))
        tk.Label(header, text=f"By {CREATOR}  |  v{VERSION}",
                 font=("Segoe UI", 10), fg=FG_MUTED, bg=BG_DARK).pack()

        btn_frame = tk.Frame(self.root, bg=BG)
        btn_frame.pack(pady=16)

        buttons = [
            ("\U0001F4CA System Health", self.system_health),
            ("\U0001F9F9 Deep Clean", self.deep_clean),
            ("\U0001F680 Startup Manager", self.startup_manager),
            ("\U0001F6E1 Malware Scan", self.malware_scan),
            ("\U0001F4E6 Bloatware Manager", self.bloatware_manager),
            ("\u2699 Service Optimizer", self.service_optimizer),
            ("\U0001F527 System Repair", self.system_repair),
            ("\u26A1 Full Optimize", self.full_optimize),
            ("\U0001F4DC View Log / Undo", self.view_log),
        ]

        for i, (text, cmd) in enumerate(buttons):
            btn = tk.Button(btn_frame, text=text, width=20, height=2,
                             font=("Segoe UI", 10, "bold"), bg=CARD, fg=FG,
                             activebackground=CARD_HOVER, activeforeground="white",
                             relief="flat", cursor="hand2", command=cmd)
            btn.grid(row=i // 3, column=i % 3, padx=8, pady=8)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=CARD_HOVER) if b["state"] != "disabled" else None)
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=CARD) if b["state"] != "disabled" else None)
            self.action_buttons.append(btn)

        # Status + progress bar
        status_frame = tk.Frame(self.root, bg=BG)
        status_frame.pack(fill="x", padx=20, pady=(0, 5))
        self.status_label = tk.Label(status_frame, text="Ready", font=("Segoe UI", 9),
                                      fg=GREEN, bg=BG, anchor="w")
        self.status_label.pack(side="left")
        self.progress = ttk.Progressbar(status_frame, mode="indeterminate", length=200)
        self.progress.pack(side="right")

        tk.Label(self.root, text="Activity Log", font=("Segoe UI", 11, "bold"),
                 fg=ACCENT, bg=BG).pack(pady=(4, 5))

        self.log_area = scrolledtext.ScrolledText(
            self.root, height=14, width=95, font=("Consolas", 9),
            bg=BG_DARK, fg=FG_MUTED, insertbackground="white", state="disabled")
        self.log_area.tag_config("error", foreground=RED)
        self.log_area.tag_config("ok", foreground=GREEN)
        self.log_area.tag_config("warn", foreground=YELLOW)
        self.log_area.pack(padx=20, pady=5)

        # Footer / links
        footer = tk.Frame(self.root, bg=BG)
        footer.pack(side="bottom", pady=10)
        for label, url in [("Website", WEBSITE), ("GitHub", GITHUB), ("Telegram", TELEGRAM)]:
            lbl = tk.Label(footer, text=label, font=("Segoe UI", 9, "underline"),
                            fg=FG_MUTED, bg=BG, cursor="hand2")
            lbl.pack(side="left", padx=10)
            lbl.bind("<Button-1>", lambda e, u=url: self.open_link(u))

    def open_link(self, url):
        webbrowser.open(url)

    # ---------- thread-safe helpers ----------
    def ui(self, func, *args, **kwargs):
        self.root.after(0, lambda: func(*args, **kwargs))

    def write_log(self, message, level="info"):
        self.ui(self._write_log_main, message, level)
        log_text(message)

    def _write_log_main(self, message, level):
        tag = {"error": "error", "ok": "ok", "warn": "warn"}.get(level, None)
        self.log_area.config(state="normal")
        if tag:
            self.log_area.insert(tk.END, f"> {message}\n", tag)
        else:
            self.log_area.insert(tk.END, f"> {message}\n")
        self.log_area.see(tk.END)
        self.log_area.config(state="disabled")

    def set_busy(self, busy, status="Ready"):
        self.busy = busy
        state = "disabled" if busy else "normal"
        for b in self.action_buttons:
            b.config(state=state)
        self.status_label.config(text=status, fg=YELLOW if busy else GREEN)
        if busy:
            self.progress.start(12)
        else:
            self.progress.stop()

    def run_task(self, func, status="Working..."):
        if self.busy:
            messagebox.showwarning("Busy", "Another task is already running. Please wait.")
            return
        self.set_busy(True, status)

        def wrapper():
            try:
                func()
            except Exception as e:
                self.write_log(f"Unexpected error: {e}", level="error")
            finally:
                self.ui(self.set_busy, False, "Ready")

        threading.Thread(target=wrapper, daemon=True).start()

    def ask_confirm(self, title, message):
        """Thread-safe blocking Yes/No dialog -- safe to call from a worker thread."""
        result = {}
        event = threading.Event()

        def ask():
            result["value"] = messagebox.askyesno(title, message)
            event.set()

        self.root.after(0, ask)
        event.wait()
        return result.get("value", False)

    def ask_selection(self, title, prompt, items, action_label="OK"):
        """Thread-safe blocking multi-select dialog. Returns list of selected
        indices, or None if cancelled."""
        result = {"value": None}
        event = threading.Event()

        def build():
            top = tk.Toplevel(self.root)
            top.title(title)
            top.configure(bg=BG)
            top.geometry("560x420")
            top.grab_set()

            tk.Label(top, text=prompt, bg=BG, fg=FG, wraplength=520,
                     justify="left", font=("Segoe UI", 10)).pack(padx=12, pady=10, anchor="w")

            frame = tk.Frame(top, bg=BG)
            frame.pack(fill="both", expand=True, padx=12)
            scrollbar = tk.Scrollbar(frame)
            scrollbar.pack(side="right", fill="y")
            lb = tk.Listbox(frame, selectmode="extended", yscrollcommand=scrollbar.set,
                             bg=BG_DARK, fg=FG, selectbackground=ACCENT,
                             font=("Consolas", 9))
            for it in items:
                lb.insert(tk.END, it)
            lb.pack(fill="both", expand=True)
            scrollbar.config(command=lb.yview)

            btn_frame = tk.Frame(top, bg=BG)
            btn_frame.pack(pady=10)

            def on_ok():
                result["value"] = list(lb.curselection())
                top.destroy()
                event.set()

            def on_cancel():
                result["value"] = None
                top.destroy()
                event.set()

            tk.Button(btn_frame, text=action_label, command=on_ok,
                      bg=CARD, fg=FG, relief="flat", padx=10).pack(side="left", padx=5)
            tk.Button(btn_frame, text="Cancel", command=on_cancel,
                      bg=CARD, fg=FG, relief="flat", padx=10).pack(side="left", padx=5)
            top.protocol("WM_DELETE_WINDOW", on_cancel)

        self.root.after(0, build)
        event.wait()
        return result["value"]

    def stream_command(self, args, module, action):
        """Run a command and stream its stdout into the log line by line.
        Returns the process return code."""
        try:
            proc = subprocess.Popen(
                args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding="utf-8", errors="ignore",
                creationflags=CREATE_NO_WINDOW,
            )
        except FileNotFoundError:
            self.write_log(f"Command not found: {args[0]}", level="error")
            return -1
        except Exception as e:
            self.write_log(f"Could not start {args[0]}: {e}", level="error")
            return -1

        for line in proc.stdout:
            line = line.strip()
            if line:
                self.write_log(line)
        proc.wait()
        log_action(module, action, f"Return code {proc.returncode}")
        return proc.returncode

    # ==================== FEATURE: System Health ====================
    def system_health(self):
        self.run_task(self._system_health_core, "Checking system health...")

    def _system_health_core(self):
        self.write_log("=== System Health Report ===")
        self.write_log(f"OS: Windows | User: {os.environ.get('USERNAME', 'unknown')} | "
                        f"Admin: {'Yes' if is_admin() else 'No'}")

        if not HAS_PSUTIL:
            self.write_log("psutil not installed -- showing basic info only "
                            "(pip install psutil for full CPU/RAM/process stats).",
                            level="warn")
        else:
            cpu = psutil.cpu_percent(interval=1)
            cores = psutil.cpu_count(logical=True)
            mem = psutil.virtual_memory()
            self.write_log(f"CPU usage: {cpu}% across {cores} logical cores")
            self.write_log(f"RAM: {human_size(mem.used)} used / {human_size(mem.total)} "
                            f"total ({mem.percent}%)")

            for part in psutil.disk_partitions(all=False):
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                except (PermissionError, OSError):
                    continue
                self.write_log(f"Disk {part.device}: {human_size(usage.used)} / "
                                f"{human_size(usage.total)} used ({usage.percent}%)")

            boot = datetime.datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.datetime.now() - boot
            self.write_log(f"Last boot: {boot.strftime('%Y-%m-%d %H:%M:%S')} "
                            f"(uptime {str(uptime).split('.')[0]})")

            procs = []
            for p in psutil.process_iter(["name", "memory_info"]):
                try:
                    procs.append((p.info["name"], p.info["memory_info"].rss))
                except (psutil.NoSuchProcess, psutil.AccessDenied, TypeError):
                    continue
            procs.sort(key=lambda x: x[1], reverse=True)
            self.write_log("Top 5 processes by RAM:")
            for name, rss in procs[:5]:
                self.write_log(f"  {name}: {human_size(rss)}")

        try:
            import shutil as _shutil
            _total, _used, free = _shutil.disk_usage("C:\\")
            self.write_log(f"C: drive free space: {human_size(free)}")
        except OSError:
            pass

        log_action("system_health", "generated", "Health report viewed")
        self.write_log("=== Report complete ===", level="ok")

    # ==================== FEATURE: Deep Clean ====================
    def deep_clean(self):
        self.run_task(self._deep_clean_core, "Scanning temp/cache folders...")

    def _deep_clean_core(self):
        targets = {
            "User TEMP": os.environ.get("TEMP", tempfile.gettempdir()),
            "Windows TEMP": r"C:\Windows\Temp",
            "Prefetch": r"C:\Windows\Prefetch",
            "Windows Update cache": r"C:\Windows\SoftwareDistribution\Download",
            "Local App TEMP": os.path.expandvars(r"%LOCALAPPDATA%\Temp"),
        }

        self.write_log("Scanning target folders...")
        sizes = {}
        for label, path in targets.items():
            size = get_folder_size(path) if os.path.isdir(path) else 0
            sizes[label] = (path, size)
            self.write_log(f"  {label}: {human_size(size)}  [{path}]")

        total = sum(s for _p, s in sizes.values())
        if total == 0:
            self.write_log("Nothing significant to clean.", level="ok")
            return

        proceed = self.ask_confirm(
            "Deep Clean",
            f"Estimated space to free: {human_size(total)}\n\n"
            f"Delete the contents of all {len(sizes)} folders listed in the log?",
        )
        if not proceed:
            self.write_log("Deep Clean cancelled -- nothing deleted.", level="warn")
            return

        grand_freed = 0
        for label, (path, _size) in sizes.items():
            if not os.path.isdir(path):
                continue
            freed, failed = 0, 0
            try:
                for entry in os.listdir(path):
                    fp = os.path.join(path, entry)
                    try:
                        if os.path.isfile(fp) or os.path.islink(fp):
                            s = os.path.getsize(fp)
                            os.remove(fp)
                            freed += s
                        elif os.path.isdir(fp):
                            s = get_folder_size(fp)
                            import shutil as _shutil
                            _shutil.rmtree(fp, ignore_errors=True)
                            freed += s
                    except OSError:
                        failed += 1
            except OSError as e:
                self.write_log(f"Could not access {label}: {e}", level="error")
                continue
            grand_freed += freed
            note = f" ({failed} items skipped, in use or no permission)" if failed else ""
            self.write_log(f"Cleaned {label}: freed {human_size(freed)}{note}",
                            level="warn" if failed else "ok")

        self.write_log(f"Deep Clean complete. Total freed: {human_size(grand_freed)}",
                        level="ok")
        log_action("deep_clean", "cleaned", f"Freed approx {human_size(grand_freed)}")

    # ==================== FEATURE: Startup Manager ====================
    def startup_manager(self):
        self.run_task(self._startup_manager_core, "Reading startup items...")

    def _list_registry_startup(self):
        items = []
        hives = [
            ("HKCU", winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            ("HKLM", winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
        ]
        for hive_name, hive, subkey in hives:
            try:
                with winreg.OpenKey(hive, subkey, 0, winreg.KEY_READ) as key:
                    i = 0
                    while True:
                        try:
                            name, value, _t = winreg.EnumValue(key, i)
                            items.append({"kind": "registry", "hive_name": hive_name,
                                          "hive": hive, "subkey": subkey,
                                          "name": name, "value": value})
                            i += 1
                        except OSError:
                            break
            except OSError:
                continue
        return items

    def _list_startup_folder(self):
        folders = [
            os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"),
            os.path.expandvars(r"%ProgramData%\Microsoft\Windows\Start Menu\Programs\Startup"),
        ]
        items = []
        for folder in folders:
            if os.path.isdir(folder):
                for name in os.listdir(folder):
                    items.append({"kind": "folder", "path": os.path.join(folder, name)})
        return items

    def _startup_manager_core(self):
        reg_items = self._list_registry_startup()
        folder_items = self._list_startup_folder()
        combined = reg_items + folder_items

        if not combined:
            self.write_log("No registry or Startup-folder entries found.", level="ok")
            return

        labels = []
        for it in combined:
            if it["kind"] == "registry":
                labels.append(f"[Registry/{it['hive_name']}] {it['name']} -> {it['value']}")
            else:
                labels.append(f"[Startup folder] {os.path.basename(it['path'])}")

        self.write_log(f"Found {len(combined)} startup item(s).")
        selected = self.ask_selection(
            "Startup Manager",
            "Select items to DISABLE. They are backed up automatically -- "
            "undo any of them later from 'View Log / Undo'.",
            labels, action_label="Disable Selected",
        )
        if not selected:
            self.write_log("Startup Manager: no changes made.")
            return

        BACKUP_DIR.mkdir(exist_ok=True)
        for i in selected:
            item = combined[i]
            if item["kind"] == "registry":
                try:
                    with winreg.OpenKey(item["hive"], item["subkey"], 0,
                                         winreg.KEY_SET_VALUE) as key:
                        winreg.DeleteValue(key, item["name"])
                    log_action("startup_manager", "disabled_registry_entry",
                               f"{item['hive_name']}\\{item['name']}",
                               undo={"type": "registry", "hive_name": item["hive_name"],
                                     "subkey": item["subkey"], "name": item["name"],
                                     "value": item["value"]})
                    self.write_log(f"Disabled: {item['name']}", level="ok")
                except OSError as e:
                    self.write_log(f"Could not disable {item['name']}: {e}", level="error")
            else:
                src = item["path"]
                dst = str(BACKUP_DIR / os.path.basename(src))
                try:
                    import shutil as _shutil
                    _shutil.move(src, dst)
                    log_action("startup_manager", "moved_startup_shortcut",
                               os.path.basename(src),
                               undo={"type": "startup_folder", "original_path": src,
                                     "backup_path": dst})
                    self.write_log(f"Moved to backup: {os.path.basename(src)}", level="ok")
                except OSError as e:
                    self.write_log(f"Could not move {src}: {e}", level="error")

    # ==================== FEATURE: Malware Scan ====================
    def malware_scan(self):
        self.run_task(self._malware_scan_core, "Preparing malware scan...")

    def _malware_scan_core(self):
        exe = find_mpcmdrun()
        if not exe:
            self.write_log("Windows Defender (MpCmdRun.exe) not found -- it may be "
                            "disabled or replaced by another antivirus.", level="error")
            return

        full = self.ask_confirm(
            "Malware Scan",
            "Run a FULL scan?\n\nYes = Full scan (thorough, can take 1+ hour)\n"
            "No = Quick scan (few minutes, checks common malware spots)",
        )
        scan_type, label = ("2", "Full") if full else ("1", "Quick")

        self.write_log(f"Starting Windows Defender {label} Scan... please wait, "
                        f"this window will not show progress until it finishes.")
        rc, _out, err = run_capture([exe, "-Scan", "-ScanType", scan_type])
        if rc == 0:
            self.write_log(f"{label} scan finished -- no errors reported.", level="ok")
        else:
            self.write_log(f"Scan exited with code {rc}. {err or ''}".strip(),
                            level="error")
        log_action("malware_scan", f"ran_{label.lower()}_scan", f"Return code {rc}")

        _rc2, out2, _err2 = run_powershell(
            "Get-MpThreatDetection | Select-Object -First 5 | Format-List")
        if out2 and out2.strip():
            self.write_log("Recent threat detections:")
            self.write_log(out2.strip())
        else:
            self.write_log("No recent threats reported by Windows Defender.")

    # ==================== FEATURE: Bloatware Manager ====================
    def bloatware_manager(self):
        self.run_task(self._bloatware_manager_core, "Scanning installed apps...")

    def _get_installed_appx(self):
        rc, out, _err = run_powershell(
            "Get-AppxPackage | Select-Object Name,PackageFullName | ConvertTo-Json -Compress",
            timeout=30,
        )
        if rc != 0 or not out:
            return []
        try:
            data = json.loads(out)
            if isinstance(data, dict):
                data = [data]
            return [(d.get("Name", ""), d.get("PackageFullName", "")) for d in data]
        except json.JSONDecodeError:
            return []

    def _bloatware_manager_core(self):
        installed = self._get_installed_appx()
        if not installed:
            self.write_log("Could not read installed packages (PowerShell unavailable "
                            "or none found).", level="error")
            return

        matches = []
        for name, full in installed:
            if any(nv.lower() in name.lower() for nv in BLOATWARE_NEVER_TOUCH):
                continue
            if any(frag.lower() in name.lower() for frag in BLOATWARE_FRAGMENTS):
                matches.append((name, full))

        if not matches:
            self.write_log("No known bloatware found on this PC.", level="ok")
            return

        self.write_log(f"Found {len(matches)} known bloatware/low-value app(s).")
        selected = self.ask_selection(
            "Bloatware Manager",
            "Select apps to REMOVE. This is NOT easily undone -- the app would "
            "need to be reinstalled from the Microsoft Store if needed later.",
            [n for n, _f in matches], action_label="Remove Selected",
        )
        if not selected:
            self.write_log("Bloatware Manager: no changes made.")
            return

        names_preview = ", ".join(matches[i][0] for i in selected)
        if not self.ask_confirm("Confirm Removal",
                                 f"Really remove:\n{names_preview}\n\nThis cannot be auto-undone."):
            self.write_log("Removal cancelled.")
            return

        for i in selected:
            name, full = matches[i]
            rc, _out, err = run_powershell(f"Remove-AppxPackage -Package '{full}'")
            if rc == 0:
                self.write_log(f"Removed: {name}", level="ok")
                log_action("bloatware_manager", "removed_appx", name,
                           undo={"note": "Reinstall from Microsoft Store if needed",
                                 "package_full_name": full})
            else:
                self.write_log(f"Failed to remove {name}: {(err or '').strip()}",
                                level="error")

    # ==================== FEATURE: Service Optimizer ====================
    def service_optimizer(self):
        self.run_task(self._service_optimizer_core, "Checking services...")

    def _get_service_start_type(self, name):
        rc, out, _err = run_capture(["sc", "qc", name])
        if rc != 0 or not out:
            return None
        for line in out.splitlines():
            if "START_TYPE" in line:
                return line.strip()
        return None

    def _service_optimizer_core(self):
        labels = []
        statuses = []
        for svc, reason in SAFE_SERVICES:
            status = self._get_service_start_type(svc)
            statuses.append(status)
            labels.append(f"{svc} -- {reason}  [{status or 'not found on this PC'}]")

        selected = self.ask_selection(
            "Service Optimizer",
            "Select services to DISABLE. These are commonly safe on a personal "
            "PC -- skip anything the client actually relies on.",
            labels, action_label="Disable Selected",
        )
        if not selected:
            self.write_log("Service Optimizer: no changes made.")
            return

        for i in selected:
            svc, reason = SAFE_SERVICES[i]
            original = statuses[i]
            rc, _out, err = run_capture(["sc", "config", svc, "start=", "disabled"])
            if rc == 0:
                self.write_log(f"Disabled service: {svc}", level="ok")
                log_action("service_optimizer", "disabled_service", svc,
                           undo={"service": svc, "original_status": original,
                                 "restore_cmd": f"sc config {svc} start= demand"})
            else:
                self.write_log(f"Could not disable {svc}: {(err or '').strip()}",
                                level="error")

    # ==================== FEATURE: System Repair ====================
    def system_repair(self):
        self.run_task(self._system_repair_core, "Preparing system repair...")

    def _system_repair_core(self):
        proceed = self.ask_confirm(
            "System Repair",
            "This runs 'sfc /scannow' and 'DISM RestoreHealth'.\n"
            "It can take 10-30+ minutes on a slow PC and needs admin rights "
            "and (for DISM) an internet connection.\n\nContinue?",
        )
        if not proceed:
            self.write_log("System Repair cancelled.")
            return

        self.write_log("Running: sfc /scannow  (this can take a while)...")
        self.stream_command(["sfc", "/scannow"], "system_repair", "ran_sfc")

        self.write_log("Running: DISM /Online /Cleanup-Image /RestoreHealth ...")
        self.stream_command(
            ["DISM", "/Online", "/Cleanup-Image", "/RestoreHealth"],
            "system_repair", "ran_dism_restorehealth",
        )
        self.write_log("System Repair finished.", level="ok")

    # ==================== FEATURE: Full Optimize ====================
    def full_optimize(self):
        if self.busy:
            messagebox.showwarning("Busy", "Another task is already running.")
            return
        proceed = messagebox.askyesno(
            "Full Optimize",
            "This runs, in order: System Health -> Deep Clean -> Startup Manager -> "
            "System Repair -> Bloatware Manager -> Defender Quick Scan.\n\n"
            "Each destructive step will still ask you to confirm. Continue?",
        )
        if not proceed:
            return
        self.run_task(self._full_optimize_core, "Running Full Optimize...")

    def _full_optimize_core(self):
        self.write_log("=== FULL OPTIMIZE: START ===", level="ok")
        self._system_health_core()
        self._deep_clean_core()
        self._startup_manager_core()
        self._system_repair_core()
        self._bloatware_manager_core()

        exe = find_mpcmdrun()
        if exe:
            self.write_log("Running Windows Defender Quick Scan...")
            rc, _out, _err = run_capture([exe, "-Scan", "-ScanType", "1"])
            self.write_log(f"Quick scan finished (code {rc}).",
                            level="ok" if rc == 0 else "error")
            log_action("full_optimize", "ran_quick_scan", f"Return code {rc}")
        self.write_log("=== FULL OPTIMIZE: COMPLETE ===", level="ok")

    # ==================== FEATURE: View Log / Undo ====================
    def view_log(self):
        entries = load_actions()
        top = tk.Toplevel(self.root)
        top.title("View Log / Undo")
        top.configure(bg=BG)
        top.geometry("640x480")

        tk.Label(top, text=f"{len(entries)} logged action(s)", bg=BG, fg=ACCENT,
                 font=("Segoe UI", 11, "bold")).pack(pady=(10, 5))

        text = scrolledtext.ScrolledText(top, height=18, width=78, bg=BG_DARK,
                                          fg=FG_MUTED, font=("Consolas", 9))
        text.pack(padx=10, pady=5, fill="both", expand=True)
        for e in entries[-50:]:
            text.insert(tk.END, f"[{e['timestamp']}] {e['module']}: "
                                 f"{e['action']} -- {e['details']}\n")
        text.config(state="disabled")

        undoable = [(i, e) for i, e in enumerate(entries) if e.get("undo")]

        def undo_last():
            if not undoable:
                messagebox.showinfo("Undo", "Nothing here can be auto-undone.")
                return
            idx, entry = undoable[-1]
            info = entry["undo"]
            try:
                if info.get("type") == "registry":
                    hive = winreg.HKEY_CURRENT_USER if info["hive_name"] == "HKCU" \
                        else winreg.HKEY_LOCAL_MACHINE
                    with winreg.OpenKey(hive, info["subkey"], 0, winreg.KEY_SET_VALUE) as key:
                        winreg.SetValueEx(key, info["name"], 0, winreg.REG_SZ, info["value"])
                    messagebox.showinfo("Undo", f"Restored startup entry: {info['name']}")
                elif info.get("type") == "startup_folder":
                    import shutil as _shutil
                    _shutil.move(info["backup_path"], info["original_path"])
                    messagebox.showinfo("Undo", "Restored startup shortcut.")
                elif "service" in info:
                    run_capture(["sc", "config", info["service"], "start=", "demand"])
                    messagebox.showinfo("Undo", f"Service '{info['service']}' set back "
                                                 f"to Manual start.")
                elif "package_full_name" in info:
                    messagebox.showinfo(
                        "Undo", f"Store apps can't be auto-reinstalled.\n"
                                f"Please reinstall '{entry['details']}' from the "
                                f"Microsoft Store manually.")
                entries[idx]["undo"] = None
                entries[idx]["details"] += " [UNDONE]"
                save_actions(entries)
                top.destroy()
                self.view_log()
            except (OSError, KeyError) as e:
                messagebox.showerror("Undo failed", str(e))

        btn_frame = tk.Frame(top, bg=BG)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text=f"Undo Most Recent ({len(undoable)} available)",
                  command=undo_last, bg=CARD, fg=FG, relief="flat", padx=10).pack()


# ==================== ENTRY POINT ====================
def main():
    if not IS_WINDOWS:
        print(f"{APP_NAME} only runs on Windows.")
        sys.exit(1)

    root = tk.Tk()
    DigiVaaniApp(root)  # noqa: kept alive by Tk callbacks bound to it

    if not is_admin():
        def prompt_elevate():
            if messagebox.askyesno(
                "Administrator recommended",
                "Some tools (Service Optimizer, DISM, some Registry edits) need "
                "Administrator rights.\n\nRestart as Administrator now?",
            ):
                if relaunch_as_admin():
                    root.destroy()
                    sys.exit(0)
                else:
                    messagebox.showwarning(
                        "Could not elevate",
                        "Please right-click the program and choose "
                        "'Run as administrator' manually.",
                    )
        root.after(400, prompt_elevate)

    root.mainloop()


if __name__ == "__main__":
    main()
