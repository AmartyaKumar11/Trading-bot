import argparse
import logging
import sys
from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException
import os
import time
from dotenv import load_dotenv


BINANCE_TESTNET_URL = "https://testnet.binancefuture.com"
LOG_FILE = "bot.log"

# Setup logging
logger = logging.getLogger("BasicBot")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

file_handler = logging.FileHandler(LOG_FILE)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

class BasicBot:
    def __init__(self, api_key, api_secret, testnet=True):
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self.client = Client(api_key, api_secret, testnet=testnet)
        self.exchange_info = self.client.futures_exchange_info()
        logger.info(f"Connected to Binance Futures {'Testnet' if testnet else 'Mainnet'}.")

    def _get_symbol_filters(self, symbol):
        for s in self.exchange_info['symbols']:
            if s['symbol'] == symbol:
                return {f['filterType']: f for f in s['filters']}
        raise ValueError(f"Symbol {symbol} not found in exchange info.")

    def _round_quantity(self, symbol, quantity):
        filters = self._get_symbol_filters(symbol)
        lot_size = filters['LOT_SIZE']
        step_size = float(lot_size['stepSize'])
        min_qty = float(lot_size['minQty'])
        max_qty = float(lot_size['maxQty'])
        quantity = max(min_qty, min(quantity, max_qty))
        rounded = round((quantity // step_size) * step_size, 8)
        return rounded

    def _round_price(self, symbol, price):
        filters = self._get_symbol_filters(symbol)
        price_filter = filters['PRICE_FILTER']
        tick_size = float(price_filter['tickSize'])
        min_price = float(price_filter['minPrice'])
        max_price = float(price_filter['maxPrice'])
        price = max(min_price, min(price, max_price))
        rounded = round((price // tick_size) * tick_size, 2)
        return rounded

    def place_market_order(self, symbol, side, quantity):
        try:
            quantity = self._round_quantity(symbol, quantity)
            logger.info(f"Placing MARKET order: {side} {quantity} {symbol}")
            response = self.client.futures_create_order(
                symbol=symbol,
                side="BUY" if side.upper() == "BUY" else "SELL",
                type="MARKET",
                quantity=quantity
            )
            logger.info(f"Order response: {response}")
            return response
        except BinanceAPIException as e:
            logger.error(f"API Error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error: {e}")
            return None

    def place_limit_order(self, symbol, side, quantity, price):
        try:
            quantity = self._round_quantity(symbol, quantity)
            price = self._round_price(symbol, price)
            logger.info(f"Placing LIMIT order: {side} {quantity} {symbol} @ {price}")
            response = self.client.futures_create_order(
                symbol=symbol,
                side="BUY" if side.upper() == "BUY" else "SELL",
                type="LIMIT",
                quantity=quantity,
                price=price,
                timeInForce="GTC"
            )
            logger.info(f"Order response: {response}")
            return response
        except BinanceAPIException as e:
            logger.error(f"API Error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error: {e}")
            return None

    def place_stop_order(self, symbol, side, quantity, stopPrice, price=None, stop_type="STOP_MARKET"):
        try:
            quantity = self._round_quantity(symbol, quantity)
            stopPrice = self._round_price(symbol, stopPrice)
            params = {
                "symbol": symbol,
                "side": "BUY" if side.upper() == "BUY" else "SELL",
                "type": stop_type,
                "quantity": quantity,
                "stopPrice": stopPrice,
            }
            if price is not None and stop_type == "STOP":
                params["price"] = self._round_price(symbol, price)
                params["timeInForce"] = "GTC"
            logger.info(f"Placing {stop_type} order: {side} {quantity} {symbol} stop @ {stopPrice} price @ {params.get('price')}")
            response = self.client.futures_create_order(**params)
            logger.info(f"Order response: {response}")
            return response
        except BinanceAPIException as e:
            logger.error(f"API Error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error: {e}")
            return None

    def change_leverage(self, symbol, leverage):
        try:
            logger.info(f"Changing leverage for {symbol} to {leverage}")
            response = self.client.futures_change_leverage(symbol=symbol, leverage=leverage)
            logger.info(f"Leverage response: {response}")
            return response
        except BinanceAPIException as e:
            logger.error(f"API Error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error: {e}")
            return None

def main():
    load_dotenv()
    parser = argparse.ArgumentParser(
        description="Binance USDT-M Futures Trading Bot",
        epilog=(
            "Example usage:\n"
            "  python bot.py order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001 --testnet\n"
            "  python bot.py order --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.01 --price 3500 --testnet\n"
            "  python bot.py order --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.001 --stopPrice 25000 --testnet\n"
        )
    )
    parser.add_argument("order", nargs="?", help="Order command")
    parser.add_argument("--symbol", default="BTCUSDT", help="Trading symbol, e.g. BTCUSDT")
    parser.add_argument("--side", default="BUY", choices=["BUY", "SELL"], help="Order side")
    parser.add_argument("--type", default="MARKET", choices=["MARKET", "LIMIT", "STOP", "STOP_MARKET"], help="Order type")
    parser.add_argument("--quantity", type=float, default=0.001, help="Order quantity")
    parser.add_argument("--price", type=float, help="Order price (for LIMIT/STOP)")
    parser.add_argument("--stopPrice", type=float, help="Stop price (for STOP/STOP_MARKET)")
    parser.add_argument("--leverage", type=int, help="Change leverage before order")
    parser.add_argument("--apiKey", help="Binance API Key")
    parser.add_argument("--apiSecret", help="Binance API Secret")
    parser.add_argument("--testnet", action="store_true", help="Use Binance Futures Testnet")
    args = parser.parse_args()

    api_key = args.apiKey or os.getenv("API_KEY")
    api_secret = args.apiSecret or os.getenv("API_SECRET")
    if not api_key or not api_secret:
        print("Error: API Key and Secret must be provided via CLI or .env file.")
        return

    bot = BasicBot(api_key, api_secret, testnet=args.testnet)

    if args.leverage:
        result = bot.change_leverage(args.symbol, args.leverage)
        print("Leverage change result:", result)

    if args.type == "MARKET":
        result = bot.place_market_order(args.symbol, args.side, args.quantity)
    elif args.type == "LIMIT":
        if not args.price:
            print("Error: --price required for LIMIT order.")
            return
        result = bot.place_limit_order(args.symbol, args.side, args.quantity, args.price)
    elif args.type in ["STOP", "STOP_MARKET"]:
        if not args.stopPrice:
            print("Error: --stopPrice required for STOP/STOP_MARKET order.")
            return
        result = bot.place_stop_order(args.symbol, args.side, args.quantity, args.stopPrice, price=args.price, stop_type=args.type)
    else:
        print("Unsupported order type.")
        return

    print("Order result:")
    print(result)

if __name__ == "__main__":
    main()
