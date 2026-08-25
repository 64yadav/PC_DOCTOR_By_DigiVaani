@echo off
REM ============================================================
REM  DigiVaani PC Doctor -- build script
REM  Run this ON WINDOWS (PyInstaller does not reliably cross-
REM  build Windows .exe files from Linux/Mac).
REM ============================================================

echo Installing/updating build dependencies...
pip install --upgrade pyinstaller psutil

echo.
echo Building DigiVaaniPCDoctor.exe ...
echo   --onefile   : single portable exe (good for a pendrive)
echo   --windowed  : no black console window behind the GUI
echo   --uac-admin : ask for Administrator rights on launch
echo.

pyinstaller --onefile --windowed --icon=PC_DOCTOR.ico --uac-admin ^
    --name DigiVaaniPCDoctor ^
    digivaani_pc_doctor.py

echo.
echo Done! Your exe is at: dist\DigiVaaniPCDoctor.exe
echo Copy that one file to your pendrive -- it needs nothing else installed.
pause
