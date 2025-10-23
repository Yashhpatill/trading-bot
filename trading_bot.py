import logging
import os
import sys
from binance import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException

def setup_logging():
    """Configures the logging system to output to console and a file."""
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File Handler
   
    try:
        file_handler = logging.FileHandler('trading_bot.log')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except PermissionError:
        print("Error: Insufficient permissions to write log file. Please check folder permissions.")
       
    except Exception as e:
        print(f"Error setting up file logger: {e}")

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO) 
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logging.info("Logging system initialized.")

class BasicBot:
    
    
    def __init__(self, api_key, api_secret, testnet=True):
        
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        
        # The base URL specified in the task requirements
        self.base_url = "https://testnet.binancefuture.com/fapi"
        
        try:
            self.client = Client(self.api_key, self.api_secret, testnet=self.testnet)
            
            logging.info("Bot initialized.")
            self.check_connection()

        except Exception as e:
            logging.error(f"Failed to initialize client: {e}")
            raise  

    def check_connection(self):
        try:
            server_time = self.client.futures_time()
            logging.info(
                f"Successfully connected to Binance Futures Testnet. "
                f"Server time: {server_time['serverTime']}"
            )
        except BinanceAPIException as e:
            logging.error(f"Failed to connect to Binance API: {e}")
            raise
        except Exception as e:
            logging.error(f"An unexpected error occurred during connection check: {e}")
            raise

    def place_market_order(self, symbol, side, quantity):
        logging.info(
            f"Attempting to place MARKET {side} order for "
            f"{quantity} {symbol}"
        )
        try:
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side.upper(),
                type='MARKET',
                quantity=str(quantity) 
            )
            logging.info(f"MARKET order successful: {order}")
            return order
        except (BinanceAPIException, BinanceOrderException) as e:
            logging.error(f"MARKET order failed: {e}")
            return {"error": str(e)}
        except Exception as e:
            logging.error(f"An unexpected error occurred placing market order: {e}")
            return {"error": str(e)}

    def place_limit_order(self, symbol, side, quantity, price):
        logging.info(
            f"Attempting to place LIMIT {side} order for "
            f"{quantity} {symbol} at {price}"
        )
        try:
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side.upper(),
                type='LIMIT',
                timeInForce='GTC', 
                quantity=str(quantity),
                price=str(price)
            )
            logging.info(f"LIMIT order successful: {order}")
            return order
        except (BinanceAPIException, BinanceOrderException) as e:
            logging.error(f"LIMIT order failed: {e}")
            return {"error": str(e)}
        except Exception as e:
            logging.error(f"An unexpected error occurred placing limit order: {e}")
            return {"error": str(e)}

    # BONUS ORDER TYPE
    def place_stop_limit_order(self, symbol, side, quantity, price, stop_price):
        logging.info(
            f"Attempting to place STOP_LIMIT {side} order for "
            f"{quantity} {symbol} at limit price {price} with stop price {stop_price}"
        )
        try:
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side.upper(),
                type='STOP_LIMIT',
                timeInForce='GTC',
                quantity=str(quantity),
                price=str(price),
                stopPrice=str(stop_price) 
            )
            logging.info(f"STOP_LIMIT order successful: {order}")
            return order
        except (BinanceAPIException, BinanceOrderException) as e:
            logging.error(f"STOP_LIMIT order failed: {e}")
            return {"error": str(e)}
        except Exception as e:
            logging.error(f"An unexpected error occurred placing stop-limit order: {e}")
            return {"error": str(e)}

# Input Validation Helper

def get_validated_input(prompt, type_converter, validator=None, error_msg="Invalid input."):
    while True:
        try:
            user_input = input(prompt).strip()
            converted_input = type_converter(user_input)
            
            if validator is None or validator(converted_input):
                return converted_input
            else:
                print(error_msg)
        except ValueError:
            print(f"Invalid format. Please try again. {error_msg}")
        except Exception as e:
            print(f"An error occurred: {e}")

# Main Application (CLI) 

def main():
    setup_logging()
    logging.info("--- Trading Bot Application Started ---")
    
    print("Welcome to the Binance Futures Testnet Trading Bot")
    print("=" * 50)
    
    api_key = os.environ.get('BINANCE_TESTNET_KEY')
    api_secret = os.environ.get('BINANCE_TESTNET_SECRET')
    
    if not api_key:
        print("API Key not found in environment variables (BINANCE_TESTNET_KEY).")
        api_key = input("Please enter your Testnet API Key: ").strip()
    
    if not api_secret:
        print("API Secret not found in environment variables (BINANCE_TESTNET_SECRET).")
        api_secret = input("Please enter your Testnet API Secret: ").strip()

    if not api_key or not api_secret:
        logging.critical("API Key or Secret is missing. Exiting.")
        print("API Key and Secret are required to run the bot. Exiting.")
        sys.exit(1)
        
    # Initialize Bot 
    try:
        bot = BasicBot(api_key, api_secret, testnet=True)
    except Exception as e:
        logging.critical(f"Failed to initialize bot. Check credentials and connection. Error: {e}")
        print(f"\nFailed to initialize bot. Please check 'trading_bot.log' for details. Exiting.")
        sys.exit(1)

    # Main Menu Loop 
    while True:
        print("\n--- Main Menu ---")
        print("1. Place Market Order")
        print("2. Place Limit Order")
        print("3. Place Stop-Limit Order (Bonus)")
        print("4. Exit")
        
        choice = input("Enter your choice (1-4): ").strip()
        
        result = None

        try:
            if choice == '1':  
                print("\n[Placing Market Order]")
                symbol = get_validated_input(
                    "Enter symbol (e.g., BTCUSDT): ", 
                    str.upper, 
                    lambda s: len(s) > 0, 
                    "Symbol cannot be empty."
                )
                side = get_validated_input(
                    "Enter side (buy/sell): ", 
                    str.lower, 
                    lambda s: s in ['buy', 'sell'], 
                    "Side must be 'buy' or 'sell'."
                )
                quantity = get_validated_input(
                    "Enter quantity (e.g., 0.001): ", 
                    float, 
                    lambda q: q > 0, 
                    "Quantity must be a positive number."
                )
                
                result = bot.place_market_order(symbol, side, quantity)

            elif choice == '2':  
                print("\n[Placing Limit Order]")
                symbol = get_validated_input(
                    "Enter symbol (e.g., BTCUSDT): ", 
                    str.upper, 
                    lambda s: len(s) > 0, 
                    "Symbol cannot be empty."
                )
                side = get_validated_input(
                    "Enter side (buy/sell): ", 
                    str.lower, 
                    lambda s: s in ['buy', 'sell'], 
                    "Side must be 'buy' or 'sell'."
                )
                quantity = get_validated_input(
                    "Enter quantity (e.g., 0.001): ", 
                    float, 
                    lambda q: q > 0, 
                    "Quantity must be a positive number."
                )
                price = get_validated_input(
                    "Enter limit price (e.g., 50000): ", 
                    float, 
                    lambda p: p > 0, 
                    "Price must be a positive number."
                )
                
                result = bot.place_limit_order(symbol, side, quantity, price)

            elif choice == '3':  
                print("\n[Placing Stop-Limit Order]")
                symbol = get_validated_input(
                    "Enter symbol (e.g., BTCUSDT): ", 
                    str.upper, 
                    lambda s: len(s) > 0, 
                    "Symbol cannot be empty."
                )
                side = get_validated_input(
                    "Enter side (buy/sell): ", 
                    str.lower, 
                    lambda s: s in ['buy', 'sell'], 
                    "Side must be 'buy' or 'sell'."
                )
                quantity = get_validated_input(
                    "Enter quantity (e.g., 0.001): ", 
                    float, 
                    lambda q: q > 0, 
                    "Quantity must be a positive number."
                )
                stop_price = get_validated_input(
                    "Enter STOP price (trigger price): ", 
                    float, 
                    lambda p: p > 0, 
                    "Stop price must be a positive number."
                )
                limit_price = get_validated_input(
                    "Enter LIMIT price (execution price): ", 
                    float, 
                    lambda p: p > 0, 
                    "Limit price must be a positive number."
                )
                
                result = bot.place_stop_limit_order(symbol, side, quantity, limit_price, stop_price)

            elif choice == '4':  
                logging.info("User selected exit. Shutting down.")
                print("Exiting. Goodbye!")
                break
                
            else:
                print("Invalid choice. Please select from 1, 2, 3, or 4.")
            
            # Output Order Status
            if result:
                print("\n--- Order Result ---")
                if "error" in result:
                    print(f"Error placing order: {result['error']}")
                else:
                    print(f"Order successfully placed!")
                    print(f"   Symbol: {result.get('symbol')}")
                    print(f"   OrderID: {result.get('orderId')}")
                    print(f"   Type: {result.get('type')}")
                    print(f"   Side: {result.get('side')}")
                    print(f"   Status: {result.get('status')}")
                    print(f"   Avg Price: {result.get('avgPrice')}")
                print("----------------------")

        except KeyboardInterrupt:
            logging.warning("Manual interruption (Ctrl+C) detected. Exiting.")
            print("\n\nCaught interrupt. Exiting gracefully.")
            break
        except Exception as e:
            logging.error(f"An unexpected error occurred in the main loop: {e}")
            print(f"An unexpected error occurred: {e}. Check the log file.")

    logging.info("--- Trading Bot Application Finished ---")

if __name__ == "__main__":
    main()