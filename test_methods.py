from binance.client import Client

api_key = "f2ab50c680fe30a0cd07b51dde309b9abc106273fe06cc593f29653c22fda32b"
api_secret = "29db2a172367de35af29cb8819a7b2c36aa80d2930caea2001229312184bb879"

print("Testing different testnet configurations...")

# Method 1: Use testnet parameter (if supported)
print("\nMethod 1: Using testnet=True parameter...")
try:
    client = Client(api_key, api_secret, testnet=True)
    info = client.futures_exchange_info()
    print("✓ Testnet=True works!")
    print(f"Found {len(info['symbols'])} trading pairs")
except Exception as e:
    print("✗ Testnet=True error:", e)

# Method 2: Manual URL override
print("\nMethod 2: Manual URL override...")
try:
    client = Client(api_key, api_secret)
    # Override both spot and futures URLs for testnet
    client.API_URL = 'https://testnet.binance.vision'
    client.FUTURES_URL = 'https://testnet.binancefuture.com'
    info = client.futures_exchange_info()
    print("✓ Manual override works!")
    print(f"Found {len(info['symbols'])} trading pairs")
except Exception as e:
    print("✗ Manual override error:", e)

# Method 3: Check if API key needs permissions
print("\nMethod 3: Testing simple ping with auth...")
try:
    client = Client(api_key, api_secret)
    client.FUTURES_URL = 'https://testnet.binancefuture.com'
    # Try a simple authenticated request
    result = client.futures_ping()
    print("✓ Authenticated ping works!")
except Exception as e:
    print("✗ Authenticated ping error:", e)
