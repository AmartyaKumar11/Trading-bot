from binance.client import Client
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")

client = Client(api_key, api_secret, testnet=True)

print("=== PLACING MORE VISIBLE TESTNET TRADES ===")

# Close existing position first
print("\n1. Closing existing BTCUSDT position...")
try:
    # Get current position
    positions = client.futures_position_information(symbol="BTCUSDT")
    current_pos = float(positions[0]['positionAmt'])
    
    if current_pos > 0:
        # Close long position with market sell
        result = client.futures_create_order(
            symbol="BTCUSDT",
            side="SELL",
            type="MARKET",
            quantity=abs(current_pos)
        )
        print(f"   ✓ Closed position: {result['orderId']}")
    else:
        print("   No position to close")
except Exception as e:
    print(f"   Error: {e}")

# Place a larger, more obvious trade
print("\n2. Placing larger test trade...")
try:
    # Place a 0.01 BTC buy order (10x larger)
    result = client.futures_create_order(
        symbol="BTCUSDT",
        side="BUY",
        type="MARKET",
        quantity=0.01
    )
    print(f"   ✓ Large order placed: {result['orderId']}")
    print(f"   Symbol: {result['symbol']}")
    print(f"   Side: {result['side']}")
    print(f"   Quantity: {result['origQty']}")
    print(f"   Status: {result['status']}")
    
    # Wait a moment then check order status
    import time
    time.sleep(2)
    
    order_status = client.futures_get_order(symbol="BTCUSDT", orderId=result['orderId'])
    print(f"   Final Status: {order_status['status']}")
    print(f"   Executed Qty: {order_status['executedQty']}")
    print(f"   Average Price: {order_status['avgPrice']}")
    
except Exception as e:
    print(f"   Error: {e}")

# Place a limit order that will stay visible
print("\n3. Placing visible limit order...")
try:
    # Get current price
    ticker = client.futures_symbol_ticker(symbol="BTCUSDT")
    current_price = float(ticker['price'])
    
    # Place limit order 5% below current price (won't fill immediately)
    limit_price = round(current_price * 0.95, 2)
    
    result = client.futures_create_order(
        symbol="BTCUSDT",
        side="BUY",
        type="LIMIT",
        quantity=0.001,
        price=limit_price,
        timeInForce="GTC"
    )
    print(f"   ✓ Limit order placed: {result['orderId']}")
    print(f"   Price: {limit_price} (current: {current_price})")
    print(f"   This order will stay visible in 'Open Orders'")
    
except Exception as e:
    print(f"   Error: {e}")

print(f"\n=== CHECK TESTNET WEB INTERFACE NOW ===")
print("Look for:")
print("- Order History (all orders)")
print("- Open Orders (active limit order)")  
print("- Positions (if market orders filled)")
print("- Portfolio/Balance changes")
