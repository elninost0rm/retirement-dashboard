@echo off
echo Building retirement_gui.exe...
pyinstaller --onefile --windowed retirement_gui.py
echo.
echo Done! Press any key to close this window.
pause >nul