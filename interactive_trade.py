#!/usr/bin/env python3
"""
Binance Futures Trading Bot - Interactive CLI
Usage: python interactive_trade.py
"""

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

class InteractiveTradingBot:
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

    def get_popular_symbols(self):
        """Get list of popular trading symbols"""
        popular = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'DOTUSDT', 
                  'LINKUSDT', 'LTCUSDT', 'BCHUSDT', 'XLMUSDT', 'EOSUSDT']
        return popular

    def _get_symbol_filters(self, symbol):
        """Get trading filters for a symbol"""
        for s in self.exchange_info['symbols']:
            if s['symbol'] == symbol:
                return {f['filterType']: f for f in s['filters']}
        return {}

    def _round_quantity(self, symbol, quantity):
        """Round quantity according to symbol's LOT_SIZE filter"""
        try:
            filters = self._get_symbol_filters(symbol)
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
                
                return round(rounded_quantity, precision)
            else:
                # Default fallback
                return round(quantity, 6)
        except Exception as e:
            logger.warning(f"Error rounding quantity for {symbol}: {e}")
            return round(quantity, 6)

    def get_symbol_price(self, symbol):
        """Get current price for symbol"""
        try:
            ticker = self.client.futures_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except:
            return None

    def show_menu(self):
        """Show main menu"""
        print("\n" + "="*50)
        print("🚀 BINANCE FUTURES TRADING BOT")
        print("="*50)
        print("1. 📈 BUY (Long Position)")
        print("2. 📉 SELL (Short Position)")
        print("3. 📊 Account Status")
        print("4. 📋 Recent Orders")
        print("5. ❌ Close Position")
        print("6. 🚪 Exit")
        print("="*50)

    def ask_symbol(self):
        """Ask user to select trading symbol"""
        popular = self.get_popular_symbols()
        
        print("\n📈 Popular Trading Pairs:")
        for i, symbol in enumerate(popular, 1):
            price = self.get_symbol_price(symbol)
            price_str = f"${price:,.2f}" if price else "N/A"
            print(f"{i:2d}. {symbol:<10} {price_str}")
        
        print(f"{len(popular)+1:2d}. Custom symbol")
        print(f"{len(popular)+2:2d}. 🚪 Exit")
        
        while True:
            try:
                choice = input(f"\nSelect symbol (1-{len(popular)+2}): ").strip().lower()
                
                # Check for exit commands
                if choice in ['exit', 'quit', 'q', str(len(popular)+2)]:
                    print("👋 Goodbye!")
                    sys.exit(0)
                
                if choice.isdigit():
                    choice = int(choice)
                    if 1 <= choice <= len(popular):
                        return popular[choice-1]
                    elif choice == len(popular)+1:
                        custom = input("Enter custom symbol (e.g., DOGEUSDT) or 'exit' to quit: ").strip().upper()
                        if custom.lower() in ['exit', 'quit', 'q']:
                            print("👋 Goodbye!")
                            sys.exit(0)
                        # Validate symbol exists
                        if self.get_symbol_price(custom):
                            return custom
                        else:
                            print("❌ Invalid symbol. Please try again.")
                    else:
                        print("❌ Invalid choice. Please try again.")
                else:
                    print("❌ Please enter a number or 'exit' to quit.")
            except (ValueError, KeyboardInterrupt):
                print("\n👋 Goodbye!")
                sys.exit(0)

    def ask_order_type(self):
        """Ask user for order type"""
        print("\n📋 Order Types:")
        print("1. 🏃 Market Order (Execute immediately at current price)")
        print("2. ⏰ Limit Order (Execute at specific price)")
        print("3. 🛑 Stop Market (Stop loss/take profit)")
        print("4. 🚪 Exit")
        
        while True:
            try:
                choice = input("Select order type (1-4): ").strip().lower()
                
                # Check for exit commands
                if choice in ['exit', 'quit', 'q', '4']:
                    print("👋 Goodbye!")
                    sys.exit(0)
                    
                if choice == "1":
                    return "MARKET"
                elif choice == "2":
                    return "LIMIT"
                elif choice == "3":
                    return "STOP_MARKET"
                else:
                    print("❌ Invalid choice. Please try again or type 'exit' to quit.")
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                sys.exit(0)

    def ask_quantity(self, symbol, side):
        """Ask user for quantity"""
        current_price = self.get_symbol_price(symbol)
        
        print(f"\n💰 Position Size for {symbol}:")
        print(f"Current price: ${current_price:,.2f}")
        print(f"⚠️  Minimum order value: $5.00")
        
        # Calculate smart suggestions based on USD value (meeting $5 minimum)
        if current_price:
            min_qty = 5.0 / current_price  # $5 worth
            suggestions = [
                round(min_qty * 1.1, 6),    # $5.50 worth
                round(min_qty * 2, 6),      # $10 worth  
                round(min_qty * 5, 6),      # $25 worth
                round(min_qty * 10, 6),     # $50 worth
            ]
        else:
            suggestions = [1.0, 5.0, 10.0, 50.0]
        
        print("\nSuggested amounts (all meet $5 minimum):")
        for i, qty in enumerate(suggestions, 1):
            value = qty * current_price if current_price else 0
            print(f"{i}. {qty} {symbol.replace('USDT', '')} (~${value:,.2f})")
        
        print(f"{len(suggestions)+1}. Custom amount")
        print(f"{len(suggestions)+2}. 🚪 Exit")
        
        while True:
            try:
                choice = input(f"\nEnter quantity or select (1-{len(suggestions)+2}): ").strip().lower()
                
                # Check for exit commands
                if choice in ['exit', 'quit', 'q', str(len(suggestions)+2)]:
                    print("👋 Goodbye!")
                    sys.exit(0)
                
                if choice.isdigit():
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(suggestions):
                        selected_qty = suggestions[choice_num-1]
                        value = selected_qty * current_price if current_price else 0
                        if value >= 5.0:
                            return selected_qty
                        else:
                            print(f"❌ Order value ${value:.2f} is below $5 minimum. Please select a larger amount.")
                    elif choice_num == len(suggestions)+1:
                        # Custom amount
                        while True:
                            try:
                                custom_input = input("Enter custom quantity or 'exit' to quit: ").strip().lower()
                                if custom_input in ['exit', 'quit', 'q']:
                                    print("👋 Goodbye!")
                                    sys.exit(0)
                                    
                                custom_qty = float(custom_input)
                                if custom_qty > 0:
                                    value = custom_qty * current_price if current_price else 0
                                    if value >= 5.0:
                                        return custom_qty
                                    else:
                                        if current_price:
                                            print(f"❌ Order value ${value:.2f} is below $5 minimum. Need at least {5.0/current_price:.6f} {symbol.replace('USDT', '')}")
                                        else:
                                            print(f"❌ Order value ${value:.2f} is below $5 minimum.")
                                else:
                                    print("❌ Quantity must be positive.")
                            except (ValueError, KeyboardInterrupt):
                                print("❌ Invalid quantity. Please enter a number or 'exit' to quit.")
                                break
                    else:
                        print(f"❌ Invalid choice. Please select 1-{len(suggestions)+2} or type 'exit' to quit.")
                else:
                    # Direct quantity input
                    try:
                        qty = float(choice)
                        if qty > 0:
                            value = qty * current_price if current_price else 0
                            if value >= 5.0:
                                return qty
                            else:
                                if current_price:
                                    print(f"❌ Order value ${value:.2f} is below $5 minimum. Need at least {5.0/current_price:.6f} {symbol.replace('USDT', '')}")
                                else:
                                    print(f"❌ Order value ${value:.2f} is below $5 minimum.")
                        else:
                            print("❌ Quantity must be positive.")
                    except ValueError:
                        print("❌ Invalid quantity. Please enter a number or 'exit' to quit.")
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                sys.exit(0)

    def ask_price(self, symbol, side):
        """Ask user for limit price"""
        current_price = self.get_symbol_price(symbol)
        
        print(f"\n💵 Limit Price for {symbol}:")
        if current_price:
            print(f"Current market price: ${current_price:,.2f}")
            
            # Suggest prices based on side
            if side.upper() == "BUY":
                suggestions = [
                    current_price * 0.99,  # 1% below
                    current_price * 0.95,  # 5% below
                    current_price * 0.90,  # 10% below
                ]
                print("Suggested BUY prices (below market):")
            else:
                suggestions = [
                    current_price * 1.01,  # 1% above
                    current_price * 1.05,  # 5% above
                    current_price * 1.10,  # 10% above
                ]
                print("Suggested SELL prices (above market):")
            
            for i, price in enumerate(suggestions, 1):
                pct = ((price - current_price) / current_price) * 100
                print(f"{i}. ${price:,.2f} ({pct:+.1f}%)")
        else:
            print("Unable to get current price")
            suggestions = []
        
        while True:
            try:
                if suggestions:
                    choice = input(f"\nEnter price or select (1-{len(suggestions)}): ").strip()
                    
                    if choice.isdigit() and 1 <= int(choice) <= len(suggestions):
                        return suggestions[int(choice)-1]
                    else:
                        price = float(choice)
                        if price > 0:
                            return price
                        else:
                            print("❌ Price must be positive.")
                else:
                    choice = input("\nEnter price: $").strip()
                    price = float(choice)
                    if price > 0:
                        return price
                    else:
                        print("❌ Price must be positive.")
            except (ValueError, KeyboardInterrupt):
                print("❌ Invalid price. Please enter a number.")

    def ask_stop_price(self, symbol, side):
        """Ask user for stop price"""
        current_price = self.get_symbol_price(symbol)
        
        print(f"\n🛑 Stop Price for {symbol}:")
        print(f"Current market price: ${current_price:,.2f}")
        
        while True:
            try:
                price = float(input("Enter stop price: $").strip())
                if price > 0:
                    return price
                else:
                    print("❌ Price must be positive.")
            except (ValueError, KeyboardInterrupt):
                print("❌ Invalid price. Please enter a number.")

    def confirm_order(self, order_details):
        """Ask user to confirm order"""
        print("\n" + "="*40)
        print("📋 ORDER CONFIRMATION")
        print("="*40)
        for key, value in order_details.items():
            print(f"{key}: {value}")
        print("="*40)
        print("Type 'exit' or 'quit' to cancel and exit")
        
        while True:
            confirm = input("Confirm order? (y/n/exit): ").strip().lower()
            if confirm in ['y', 'yes']:
                return True
            elif confirm in ['n', 'no']:
                return False
            elif confirm in ['exit', 'quit', 'q']:
                print("👋 Goodbye!")
                sys.exit(0)
            else:
                print("❌ Please enter 'y', 'n', or 'exit'")

    def place_order(self, symbol, side, order_type, quantity, price=None, stop_price=None):
        """Place the order"""
        try:
            # Round quantity to proper precision
            quantity = self._round_quantity(symbol, quantity)
            
            params = {
                'symbol': symbol,
                'side': side,
                'type': order_type,
                'quantity': quantity
            }
            
            if order_type == "LIMIT":
                params['price'] = price
                params['timeInForce'] = 'GTC'
            elif order_type == "STOP_MARKET":
                params['stopPrice'] = stop_price
            
            result = self.client.futures_create_order(**params)
            
            print(f"\n✅ Order placed successfully!")
            print(f"Order ID: {result['orderId']}")
            print(f"Status: {result['status']}")
            print(f"Quantity: {result['origQty']} (rounded from {quantity})")
            
            return result
            
        except BinanceAPIException as e:
            print(f"❌ API Error: {e}")
            return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None

    def show_status(self):
        """Show account status"""
        try:
            account = self.client.futures_account()
            balance = account.get('totalWalletBalance', '0')
            available = account.get('availableBalance', '0')
            
            print(f"\n💰 Balance: {balance} USDT")
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
                    print(f"   {symbol}: {side} {abs(float(size))} @ ${entry} (PnL: ${pnl})")
            else:
                print("\n📊 No active positions")
                
        except Exception as e:
            print(f"❌ Error getting status: {e}")

    def show_orders(self):
        """Show recent orders"""
        symbol = self.ask_symbol()
        try:
            orders = self.client.futures_get_all_orders(symbol=symbol, limit=10)
            print(f"\n📋 Recent {symbol} Orders:")
            for order in orders[-5:]:
                status_emoji = "✅" if order['status'] == 'FILLED' else "⏳" if order['status'] == 'NEW' else "❌"
                price = order.get('avgPrice') if order.get('avgPrice') != '0' else order['price']
                print(f"   {status_emoji} {order['side']} {order['origQty']} @ ${price} [{order['status']}]")
        except Exception as e:
            print(f"❌ Error getting orders: {e}")

    def close_position(self):
        """Close position"""
        symbol = self.ask_symbol()
        try:
            positions = self.client.futures_position_information(symbol=symbol)
            current_pos = float(positions[0]['positionAmt'])
            
            if current_pos == 0:
                print(f"ℹ️  No position to close for {symbol}")
                return
            
            side = "SELL" if current_pos > 0 else "BUY"
            
            order_details = {
                'Symbol': symbol,
                'Action': f'Close {side} Position',
                'Quantity': abs(current_pos),
                'Type': 'Market Order'
            }
            
            if self.confirm_order(order_details):
                result = self.place_order(symbol, side, "MARKET", abs(current_pos))
                if result:
                    print(f"✅ Closed {symbol} position")
            
        except Exception as e:
            print(f"❌ Error closing position: {e}")

    def run(self):
        """Main interactive loop"""
        print("🎉 Welcome to Binance Futures Trading Bot!")
        
        while True:
            try:
                self.show_menu()
                choice = input("\nSelect option (1-6): ").strip()
                
                if choice == "1" or choice == "2":
                    side = "BUY" if choice == "1" else "SELL"
                    
                    symbol = self.ask_symbol()
                    if not symbol:
                        continue
                        
                    order_type = self.ask_order_type()
                    if not order_type:
                        continue
                        
                    quantity = self.ask_quantity(symbol, side)
                    if not quantity:
                        continue
                    
                    price = None
                    stop_price = None
                    
                    if order_type == "LIMIT":
                        price = self.ask_price(symbol, side)
                    elif order_type == "STOP_MARKET":
                        stop_price = self.ask_stop_price(symbol, side)
                    
                    # Prepare order details for confirmation
                    order_details = {
                        'Symbol': symbol,
                        'Side': side,
                        'Type': order_type,
                        'Quantity': quantity
                    }
                    
                    if price:
                        order_details['Price'] = f"${price:,.2f}"
                    if stop_price:
                        order_details['Stop Price'] = f"${stop_price:,.2f}"
                    
                    if self.confirm_order(order_details):
                        self.place_order(symbol, side, order_type, quantity, price, stop_price)
                
                elif choice == "3":
                    self.show_status()
                
                elif choice == "4":
                    self.show_orders()
                
                elif choice == "5":
                    self.close_position()
                
                elif choice == "6":
                    print("👋 Goodbye!")
                    break
                
                else:
                    print("❌ Invalid choice. Please try again.")
                
                input("\nPress Enter to continue...")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    bot = InteractiveTradingBot(testnet=True)
    bot.run()
