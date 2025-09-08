@echo off
REM Simple runner for Binance Futures Testnet bot
REM Edit the symbol, side, type, and quantity as needed

set SYMBOL=BTCUSDT
set SIDE=BUY
set TYPE=MARKET
set QUANTITY=0.001
set TESTNET=--testnet

REM Run the bot using the virtual environment's Python
"%~dp0.venv\Scripts\python.exe" bot.py order --symbol %SYMBOL% --side %SIDE% --type %TYPE% --quantity %QUANTITY% %TESTNET%
pause
