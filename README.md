<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=32&duration=3000&pause=1000&color=00FF9C&center=true&vCenter=true&width=600&lines=DigiVaani+PC+Doctor;Diagnose.+Clean.+Repair.+Repeat.;Built+for+Real+Technicians." alt="Typing SVG" />

<br>

![Platform](https://img.shields.io/badge/platform-Windows%2010%20%7C%2011-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![Python](https://img.shields.io/badge/python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-00C853?style=for-the-badge)
![Made by](https://img.shields.io/badge/made%20by-DigiVaani64-FF4B4B?style=for-the-badge)

<br>

**A portable, menu-driven Windows PC health, cleanup & repair tool** — built by
[**Ranjeet Yadav (64yadav)**](https://github.com/64yadav) under the **DigiVaani64** brand.

<img src="https://user-images.githubusercontent.com/74038190/212284100-561aa473-3905-4a80-b561-0d28506553ee.gif" width="100%">

</div>

---

### ⚡ Why this exists

Runs as a single `.exe` from a USB pendrive. No installer, no bundled third-party antivirus engine —
it only drives **Windows' own built-in tools** (Windows Defender, SFC, DISM, PowerShell App-x cmdlets,
Service Control, Registry) through a simple GUI, so a non-technical user can hand it to a technician
and know **exactly** what it will touch.

<br>

## 📋 Table of Contents

- [Features](#-features)
- [Requirements](#-requirements)
- [Build the .exe](#️-build-the-exe-yourself)
- [Admin Rights](#-admin-rights)
- [Safety Design](#-safety-design)
- [License](#-license)
- [Links](#-links)

<br>

## 🚀 Features

<table>
<tr><th width="35%">Module</th><th>What it does</th></tr>
<tr><td>🩺 <b>System Health Report</b></td><td>CPU / RAM / disk usage, uptime, top processes by RAM</td></tr>
<tr><td>🧹 <b>Deep Clean</b></td><td>Frees space from Temp, Prefetch, Windows Update cache, etc. — shows an estimate and asks for confirmation before deleting anything</td></tr>
<tr><td>🛫 <b>Startup Manager</b></td><td>Lists Registry <code>Run</code> keys + Startup-folder shortcuts, lets you disable selected ones (auto-backed up so you can undo)</td></tr>
<tr><td>🛡️ <b>Malware Scan</b></td><td>Triggers a real Windows Defender Quick or Full scan and reports the result</td></tr>
<tr><td>📦 <b>Bloatware Manager</b></td><td>Detects common OEM/low-value Store apps and can remove selected ones</td></tr>
<tr><td>⚙️ <b>Service Optimizer</b></td><td>Curated, conservative list of Windows services that are commonly safe to disable on a personal PC</td></tr>
<tr><td>🔧 <b>System Repair</b></td><td>Runs <code>sfc /scannow</code> and <code>DISM /RestoreHealth</code>, output streamed live</td></tr>
<tr><td>⚡ <b>Full Optimize</b></td><td>Runs the above in a sensible order, still asking before anything destructive</td></tr>
<tr><td>📜 <b>View Log / Undo</b></td><td>Every reversible change (startup items, services) is logged and can be undone from here</td></tr>
</table>

<br>

## 💻 Requirements

- Windows 10 or 11
- To just **run** the built `.exe`: nothing else — it's fully self-contained
- To **build from source**: Python 3.10+, then:
  ```bash
  pip install -r requirements.txt
  ```

<br>

## 🛠️ Build the .exe yourself

> Run on a Windows machine — PyInstaller does not reliably cross-build Windows executables from Linux/Mac.

**Option A — one click:**
```bash
build_exe.bat
```

**Option B — manual:**
```bash
pyinstaller --onefile --windowed --uac-admin --name DigiVaaniPCDoctor digivaani_pc_doctor.py
```

The finished exe lands at `dist\DigiVaaniPCDoctor.exe` — copy that single file to a pendrive. ✅

<details>
<summary>⚠️ <b>SmartScreen warning? Click here</b></summary>
<br>

Since this app is unsigned (no paid code-signing certificate), Windows SmartScreen will likely show a
**"Windows protected your PC"** warning the first time someone runs it.

➡️ Click **More info → Run anyway**.

This is completely normal for independently published tools and is **not** a sign of a problem.

</details>

<br>

## 🔐 Admin Rights

Several features (Service Optimizer, DISM, some registry edits) need **Administrator privileges**.

- The `.exe` is built with a UAC manifest → Windows prompts for elevation automatically
- Running the `.py` file directly → the app offers to relaunch itself as Administrator on startup

<br>

## 🛡️ Safety Design

- ✅ Nothing destructive runs without a preview + explicit confirmation
- ✅ Startup and service changes are logged with enough detail to undo them
- ✅ A curated **"never touch"** list protects core Windows components from the Bloatware Manager
- ✅ No blind auto-delete, anywhere

<br>

## 📄 License

Released under the **MIT License** — see [LICENSE](LICENSE) for details.

<br>

## 🔗 Links

<div align="left">

[![Website](https://img.shields.io/badge/Website-64yadav.github.io%2FDigiVaani-2ea44f?style=for-the-badge&logo=googlechrome&logoColor=white)](https://64yadav.github.io/DigiVaani)
[![GitHub](https://img.shields.io/badge/GitHub-64yadav-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/64yadav)
[![Telegram](https://img.shields.io/badge/Telegram-DigiVaani-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/DigiVaani)

</div>

<br>

---

<div align="center">

**Built with ❤️ by DigiVaani64 — bringing simple, reliable tools to every desktop.**

<img src="https://user-images.githubusercontent.com/74038190/212284158-e840e285-664b-44d7-b79b-e264b5e54825.gif" width="100">

</div>
