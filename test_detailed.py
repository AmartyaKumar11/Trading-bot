import requests
from binance.client import Client

api_key = "f2ab50c680fe30a0cd07b51dde309b9abc106273fe06cc593f29653c22fda32b"
api_secret = "29db2a172367de35af29cb8819a7b2c36aa80d2930caea2001229312184bb879"

# Test 1: Check if testnet is reachable
print("Test 1: Checking testnet connectivity...")
try:
    response = requests.get("https://testnet.binancefuture.com/fapi/v1/ping", timeout=10)
    print(f"Testnet ping: {response.status_code}")
    if response.status_code == 200:
        print("✓ Testnet is reachable")
    else:
        print("✗ Testnet returned error:", response.text)
except Exception as e:
    print("✗ Cannot reach testnet:", e)

# Test 2: Test exchange info without authentication
print("\nTest 2: Checking exchange info (no auth)...")
try:
    response = requests.get("https://testnet.binancefuture.com/fapi/v1/exchangeInfo", timeout=10)
    print(f"Exchange info: {response.status_code}")
    if response.status_code == 200:
        print("✓ Exchange info works without auth")
    else:
        print("✗ Exchange info failed:", response.text)
except Exception as e:
    print("✗ Exchange info error:", e)

# Test 3: Test with python-binance
print("\nTest 3: Testing with python-binance...")
try:
    client = Client(api_key, api_secret)
    client.FUTURES_URL = "https://testnet.binancefuture.com"
    info = client.futures_exchange_info()
    print("✓ Python-binance works!")
    print(f"Found {len(info['symbols'])} trading pairs")
except Exception as e:
    print("✗ Python-binance error:", e)

# Test 4: Test account info (requires valid API key)
print("\nTest 4: Testing account info (requires valid API key)...")
try:
    client = Client(api_key, api_secret)
    client.FUTURES_URL = "https://testnet.binancefuture.com"
    account = client.futures_account()
    print("✓ Account info works!")
    print(f"Account balance: {account.get('totalWalletBalance', 'N/A')}")
except Exception as e:
    print("✗ Account info error:", e)
