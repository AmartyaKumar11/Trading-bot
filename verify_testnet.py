from binance.client import Client
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")

client = Client(api_key, api_secret, testnet=True)

print("=== TESTNET VERIFICATION ===")

# 1. Check account info
print("\n1. Account Information:")
try:
    account = client.futures_account()
    print(f"   Account Balance: {account.get('totalWalletBalance', 'N/A')} USDT")
    print(f"   Available Balance: {account.get('availableBalance', 'N/A')} USDT")
    print("   ✓ Connected to TESTNET account")
except Exception as e:
    print(f"   ✗ Error: {e}")

# 2. Check recent orders
print("\n2. Recent Orders:")
try:
    orders = client.futures_get_all_orders(symbol="BTCUSDT", limit=5)
    for order in orders[-3:]:  # Show last 3 orders
        print(f"   Order ID: {order['orderId']}")
        print(f"   Symbol: {order['symbol']}")
        print(f"   Side: {order['side']}")
        print(f"   Type: {order['type']}")
        print(f"   Quantity: {order['origQty']}")
        print(f"   Status: {order['status']}")
        print(f"   Time: {order['time']}")
        print("   ---")
except Exception as e:
    print(f"   ✗ Error: {e}")

# 3. Check specific order (your last order)
order_id = 5642576716
print(f"\n3. Checking Order ID {order_id}:")
try:
    order = client.futures_get_order(symbol="BTCUSDT", orderId=order_id)
    print(f"   Status: {order['status']}")
    print(f"   Executed Qty: {order['executedQty']}")
    print(f"   Average Price: {order['avgPrice']}")
    print(f"   Time: {order['time']}")
    print("   ✓ Order found on TESTNET")
except Exception as e:
    print(f"   ✗ Error: {e}")

# 4. Check positions
print("\n4. Current Positions:")
try:
    positions = client.futures_position_information()
    active_positions = [pos for pos in positions if float(pos['positionAmt']) != 0]
    if active_positions:
        for pos in active_positions:
            print(f"   Symbol: {pos['symbol']}")
            print(f"   Size: {pos['positionAmt']}")
            print(f"   Entry Price: {pos['entryPrice']}")
            print(f"   PnL: {pos['unRealizedProfit']}")
            print("   ---")
    else:
        print("   No active positions")
        print("   ✓ Clean testnet account")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n=== TESTNET VERIFICATION COMPLETE ===")
