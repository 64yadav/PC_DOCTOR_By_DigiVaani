# DigiVaani PC Doctor

A portable, menu-driven Windows PC health, cleanup & repair tool — built by
[Ranjeet Yadav (64yadav)](https://github.com/64yadav) under the
**DigiVaani64** brand.

Runs as a single `.exe` from a USB pendrive. No installer, no bundled
third-party antivirus engine — it only drives Windows' own built-in tools
(Windows Defender, SFC, DISM, PowerShell App-x cmdlets, Service Control,
Registry) through a simple GUI, so a non-technical user can hand it to a
technician and know exactly what it will touch.

## Features

| Module | What it does |
|---|---|
| System Health Report | CPU / RAM / disk usage, uptime, top processes by RAM |
| Deep Clean | Frees space from Temp, Prefetch, Windows Update cache, etc. — shows an estimate and asks for confirmation before deleting anything |
| Startup Manager | Lists Registry `Run` keys + Startup-folder shortcuts, lets you disable selected ones (auto-backed up so you can undo) |
| Malware Scan | Triggers a real Windows Defender Quick or Full scan and reports the result |
| Bloatware Manager | Detects common OEM/low-value Store apps and can remove selected ones |
| Service Optimizer | Curated, conservative list of Windows services that are commonly safe to disable on a personal PC |
| System Repair | Runs `sfc /scannow` and `DISM /RestoreHealth`, output streamed live |
| Full Optimize | Runs the above in a sensible order, still asking before anything destructive |
| View Log / Undo | Every reversible change (startup items, services) is logged and can be undone from here |

## Requirements

- Windows 10 or 11
- To just **run** the built `.exe`: nothing else — it's fully self-contained
- To **build from source**: Python 3.10+, then:
  ```
  pip install -r requirements.txt
  ```

## Build the .exe yourself

Run on a Windows machine (PyInstaller does not reliably cross-build Windows
executables from Linux/Mac):

```
build_exe.bat
```

or manually:

```
pyinstaller --onefile --windowed --uac-admin --name DigiVaaniPCDoctor digivaani_pc_doctor.py
```

The finished exe is at `dist\DigiVaaniPCDoctor.exe` — copy that single file
to a pendrive.

> **Note:** Since this app is unsigned (no paid code-signing certificate),
> Windows SmartScreen will likely show a "Windows protected your PC" warning
> the first time someone runs it. Click **More info → Run anyway**. This is
> normal for independently published tools and not a sign of a problem.

## Admin rights

Several features (Service Optimizer, DISM, some registry edits) need
Administrator privileges. The exe is built with a UAC manifest so Windows
will prompt for elevation automatically; if you run the `.py` file directly
instead, the app will offer to relaunch itself as Administrator on startup.

## Safety design

- Nothing destructive runs without a preview + explicit confirmation
- Startup and service changes are logged with enough detail to undo them
- A curated "never touch" list protects core Windows components from the
  Bloatware Manager
- No blind auto-delete anywhere

## License

MIT — see [LICENSE](LICENSE).

## Links

- Website: https://64yadav.github.io/DigiVaani
- GitHub: https://github.com/64yadav
- Telegram: _add your link here_
