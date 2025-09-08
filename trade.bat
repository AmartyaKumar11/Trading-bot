@echo off
REM Wrapper script for easy trading commands
REM Usage: trade [command] [options]

if "%VIRTUAL_ENV%"=="" (
    echo ❌ Virtual environment not activated. Run 'activate.bat' first.
    exit /b 1
)

python "%~dp0trade.py" %*
