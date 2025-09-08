from binance.client import Client
import os
from dotenv import load_dotenv

load_dotenv()
client = Client(os.getenv('API_KEY'), os.getenv('API_SECRET'), testnet=True)

# Test the rounding function 
def test_round_quantity(symbol, quantity):
    # Get exchange info
    exchange_info = client.futures_exchange_info()
    
    # Get symbol filters
    symbol_info = next(s for s in exchange_info['symbols'] if s['symbol'] == symbol)
    filters = {f['filterType']: f for f in symbol_info['filters']}
    
    if 'LOT_SIZE' in filters:
        lot_size = filters['LOT_SIZE']
        step_size = float(lot_size['stepSize'])
        min_qty = float(lot_size['minQty'])
        max_qty = float(lot_size['maxQty'])
        
        # Ensure quantity is within bounds
        quantity = max(min_qty, min(quantity, max_qty))
        
        # Round UP to next valid step to meet minimum $5 requirement
        steps = quantity / step_size
        rounded_steps = int(steps) if steps == int(steps) else int(steps) + 1
        rounded_quantity = rounded_steps * step_size
        
        # Determine precision based on step_size
        if step_size >= 1:
            precision = 0
        else:
            precision = len(str(step_size).split('.')[-1])
        
        result = round(rounded_quantity, precision)
        
        print(f"Symbol: {symbol}")
        print(f"Original quantity: {quantity}")
        print(f"Step size: {step_size}")
        print(f"Rounded quantity: {result}")
        print(f"Steps: {steps} -> {rounded_steps}")
        print(f"Precision: {precision}")
        print("-" * 40)
        
        return result

# Test with LINKUSDT
price = float(client.futures_symbol_ticker(symbol='LINKUSDT')['price'])
min_qty_for_5usd = 5.0 / price

print(f"LINKUSDT price: ${price}")
print(f"Min qty for $5: {min_qty_for_5usd}")
print("=" * 40)

rounded_qty = test_round_quantity('LINKUSDT', min_qty_for_5usd)
final_value = rounded_qty * price
print(f"Final quantity: {rounded_qty}")
print(f"Final value: ${final_value:.2f}")

# Test a market buy order with the rounded quantity
print("\nTesting order placement...")
try:
    result = client.futures_create_order(
        symbol='LINKUSDT',
        side='BUY',
        type='MARKET',
        quantity=rounded_qty
    )
    print(f"✅ Order successful! Order ID: {result['orderId']}")
    print(f"Executed quantity: {result['executedQty']}")
    print(f"Status: {result['status']}")
except Exception as e:
    print(f"❌ Order failed: {e}")
