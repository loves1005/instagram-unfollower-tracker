@echo off
cd /d "%~dp0"
echo Starting Instagram Unfollower Tracker...
"C:\Users\loves\AppData\Local\Programs\Python\Python314\python.exe" main.py
if %errorlevel% neq 0 (
    echo.
    echo --------------------------------------------------
    echo [ERROR] The app failed to start (Error Code: %errorlevel%).
    echo Please take a screenshot of this window and let me know.
    echo --------------------------------------------------
    pause
)
