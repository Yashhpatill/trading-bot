# Binance Futures Testnet Trading Bot Assignment

## Description
A Python script developed as part of a job application task. This bot interacts with the Binance Futures Testnet API to place Market, Limit, and Stop-Limit orders via a command-line interface.

## Features
- Connects to Binance Futures Testnet API.
- Places Market orders (BUY/SELL).
- Places Limit orders (BUY/SELL).
- Places Stop-Limit orders (BUY/SELL).
- Command-line interface (CLI) for user input.
- Validates user input.
- Logs API requests, responses, and errors to `trading_bot.log` and console.
- Basic error handling for API exceptions.


 ## Important Note
During development, persistent browser redirection issues prevented access to testnet.binancefuture.com for generating API keys with 'Enable Futures' permissions. The included trading_bot.log reflects execution attempts using keys generated from demo.binance.com, resulting in expected API permission errors (e.g., -1022, -2015) during order placement attempts. The core script logic for order creation, input handling, and logging functions as required by the assignment.
