@echo off
echo Activating trading bot environment...
call "%~dp0.venv\Scripts\activate.bat"
echo.
echo ✅ Environment activated! You can now use:
echo   trade buy
echo   trade sell  
echo   trade status
echo   trade orders
echo   trade close
echo.
echo Type 'deactivate' to exit
cmd /k
