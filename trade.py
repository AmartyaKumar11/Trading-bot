#!/usr/bin/env python3
"""
Binance Futures Trading Bot - Interactive CLI
Usage: python trade.py [command] [options]
"""

import argparse
import os
import sys
from binance.client import Client
from binance.exceptions import BinanceAPIException
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

class TradingBot:
    def __init__(self, testnet=True):
        self.api_key = os.getenv("API_KEY")
        self.api_secret = os.getenv("API_SECRET")
        
        if not self.api_key or not self.api_secret:
            print("❌ Error: API_KEY and API_SECRET not found in .env file")
            sys.exit(1)
        
        self.testnet = testnet
        self.client = Client(self.api_key, self.api_secret, testnet=testnet)
        
        # Get exchange info for validation
        try:
            self.exchange_info = self.client.futures_exchange_info()
            env_name = "TESTNET" if testnet else "MAINNET"
            print(f"✅ Connected to Binance Futures {env_name}")
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            sys.exit(1)

    def buy(self, symbol="BTCUSDT", amount=0.001, price=None):
        """Place a BUY order"""
        if price:
            return self._place_limit_order(symbol, "BUY", amount, price)
        else:
            return self._place_market_order(symbol, "BUY", amount)

    def sell(self, symbol="BTCUSDT", amount=0.001, price=None):
        """Place a SELL order"""
        if price:
            return self._place_limit_order(symbol, "SELL", amount, price)
        else:
            return self._place_market_order(symbol, "SELL", amount)

    def status(self):
        """Show account status"""
        try:
            account = self.client.futures_account()
            balance = account.get('totalWalletBalance', '0')
            available = account.get('availableBalance', '0')
            
            print(f"💰 Balance: {balance} USDT")
            print(f"💳 Available: {available} USDT")
            
            # Show positions
            positions = self.client.futures_position_information()
            active_positions = [pos for pos in positions if float(pos['positionAmt']) != 0]
            
            if active_positions:
                print("\n📊 Active Positions:")
                for pos in active_positions:
                    size = pos['positionAmt']
                    symbol = pos['symbol']
                    entry = pos['entryPrice']
                    pnl = pos['unRealizedProfit']
                    side = "LONG" if float(size) > 0 else "SHORT"
                    print(f"   {symbol}: {side} {abs(float(size))} @ {entry} (PnL: {pnl})")
            else:
                print("\n📊 No active positions")
                
        except Exception as e:
            print(f"❌ Error getting status: {e}")

    def orders(self, symbol="BTCUSDT", limit=5):
        """Show recent orders"""
        try:
            orders = self.client.futures_get_all_orders(symbol=symbol, limit=limit)
            print(f"\n📋 Recent {symbol} Orders:")
            for order in orders[-limit:]:
                status_emoji = "✅" if order['status'] == 'FILLED' else "⏳" if order['status'] == 'NEW' else "❌"
                print(f"   {status_emoji} {order['side']} {order['origQty']} @ {order.get('avgPrice', order['price'])} [{order['status']}]")
        except Exception as e:
            print(f"❌ Error getting orders: {e}")

    def close(self, symbol="BTCUSDT"):
        """Close position for symbol"""
        try:
            positions = self.client.futures_position_information(symbol=symbol)
            current_pos = float(positions[0]['positionAmt'])
            
            if current_pos == 0:
                print(f"ℹ️  No position to close for {symbol}")
                return
            
            side = "SELL" if current_pos > 0 else "BUY"
            result = self._place_market_order(symbol, side, abs(current_pos))
            if result:
                print(f"✅ Closed {symbol} position")
            
        except Exception as e:
            print(f"❌ Error closing position: {e}")

    def _place_market_order(self, symbol, side, quantity):
        try:
            result = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type="MARKET",
                quantity=quantity
            )
            
            status_emoji = "✅" if result['status'] == 'FILLED' else "⏳"
            print(f"{status_emoji} {side} {quantity} {symbol} [Market] - Order ID: {result['orderId']}")
            return result
            
        except BinanceAPIException as e:
            print(f"❌ API Error: {e}")
            return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None

    def _place_limit_order(self, symbol, side, quantity, price):
        try:
            result = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type="LIMIT",
                quantity=quantity,
                price=price,
                timeInForce="GTC"
            )
            
            print(f"⏳ {side} {quantity} {symbol} @ {price} [Limit] - Order ID: {result['orderId']}")
            return result
            
        except BinanceAPIException as e:
            print(f"❌ API Error: {e}")
            return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None

def main():
    parser = argparse.ArgumentParser(
        prog='trade',
        description='🚀 Binance Futures Trading Bot',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  trade buy                          # Buy 0.001 BTCUSDT (market)
  trade buy --amount 0.01            # Buy 0.01 BTCUSDT
  trade buy --symbol ETHUSDT         # Buy 0.001 ETHUSDT
  trade buy --price 50000            # Buy 0.001 BTCUSDT @ 50000 (limit)
  trade sell --amount 0.005          # Sell 0.005 BTCUSDT
  trade status                       # Show account info
  trade orders                       # Show recent orders
  trade close                        # Close BTCUSDT position
  trade close --symbol ETHUSDT       # Close ETHUSDT position
        """
    )
    
    # Main command
    parser.add_argument('command', choices=['buy', 'sell', 'status', 'orders', 'close'], 
                       help='Trading command')
    
    # Optional arguments
    parser.add_argument('--symbol', '-s', default='BTCUSDT', 
                       help='Trading symbol (default: BTCUSDT)')
    parser.add_argument('--amount', '-a', type=float, default=0.001, 
                       help='Order amount (default: 0.001)')
    parser.add_argument('--price', '-p', type=float, 
                       help='Limit price (if not specified, uses market order)')
    parser.add_argument('--mainnet', action='store_true', 
                       help='Use mainnet (default: testnet)')
    
    args = parser.parse_args()
    
    # Initialize bot
    bot = TradingBot(testnet=not args.mainnet)
    
    # Execute command
    if args.command == 'buy':
        bot.buy(args.symbol, args.amount, args.price)
    elif args.command == 'sell':
        bot.sell(args.symbol, args.amount, args.price)
    elif args.command == 'status':
        bot.status()
    elif args.command == 'orders':
        bot.orders(args.symbol)
    elif args.command == 'close':
        bot.close(args.symbol)

if __name__ == "__main__":
    main()
