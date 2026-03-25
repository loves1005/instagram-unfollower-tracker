@echo off
cd /d "%~dp0"
echo.
echo [1/2] 파이썬 설치 상태 확인 중...
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [오류] 'python' 명령어를 찾을 수 없습니다. 파이썬이 설치되어 있는지 확인해 주세요.
    pause
    exit /b
)

echo [2/2] 인스타그램 맞팔 확인기 실행 중...
python main.py
if %errorlevel% neq 0 (
    echo.
    echo --------------------------------------------------
    echo [오류] 앱 실행에 실패했습니다 (에러 코드: %errorlevel%).
    echo --------------------------------------------------
    pause
)
