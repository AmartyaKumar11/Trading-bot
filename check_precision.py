from binance.client import Client
import os
from dotenv import load_dotenv

load_dotenv()
client = Client(os.getenv('API_KEY'), os.getenv('API_SECRET'), testnet=True)

# Get LINKUSDT info
info = client.futures_exchange_info()
symbol_info = next(s for s in info['symbols'] if s['symbol'] == 'LINKUSDT')
lot_size = next(f for f in symbol_info['filters'] if f['filterType'] == 'LOT_SIZE')

print(f"LINKUSDT LOT_SIZE filter: {lot_size}")

# Get current price
price = float(client.futures_symbol_ticker(symbol='LINKUSDT')['price'])
min_qty_for_5usd = 5.0 / price
step_size = float(lot_size['stepSize'])

# Round up to next valid step
rounded_qty = ((min_qty_for_5usd // step_size) + 1) * step_size
rounded_qty = round(rounded_qty, 3)  # Round to 3 decimals for LINK

print(f"Price: ${price}")
print(f"Min qty for $5: {min_qty_for_5usd}")
print(f"Step size: {step_size}")
print(f"Properly rounded qty: {rounded_qty}")
print(f"Value: ${rounded_qty * price:.2f}")
print(f"Valid example: 0.250 LINK = ${0.250 * price:.2f}")
print(f"Valid example: 0.500 LINK = ${0.500 * price:.2f}")
