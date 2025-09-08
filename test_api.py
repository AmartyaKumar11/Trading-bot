from binance.client import Client

api_key = "f2ab50c680fe30a0cd07b51dde309b9abc106273fe06cc593f29653c22fda32b"
api_secret = "29db2a172367de35af29cb8819a7b2c36aa80d2930caea2001229312184bb879"

client = Client(api_key, api_secret)
client.FUTURES_URL = "https://testnet.binancefuture.com"

try:
    info = client.futures_exchange_info()
    print("Exchange info fetched successfully!")
    print(info)
except Exception as e:
    print("Error:", e)
