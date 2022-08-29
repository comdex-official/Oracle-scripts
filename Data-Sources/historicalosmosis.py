#!/usr/bin/env python3
import requests
import sys

# URL to fetch historical data for a specific token using osmosis api
URL = "https://api-osmosis.imperator.co/tokens/v2/historical/{}/chart?tf=5"
HEADER = { "Accept": "application/json"}

def get_historical_price(symbols):
    prices = []
    for symbol in symbols:
        # Add symbol to URL
        url = URL.format(symbol)
        # Request data
        req = requests.get(url, headers=HEADER)
        if req.status_code != 200:
            raise Exception(f"Unable to fetch price: {symbol=}")
        prices.append(list(map(lambda x: x['close'], req.json()[-6:])))
    return prices

def median(prices):
    prices.sort()
    length = len(prices)
    mid = length//2
    if length % 2 == 1:
        val = prices[mid]
    else:
        val = (prices[mid] + prices[mid+1])/2
    return round(val, 6)

def main(args):
    length = len(args)
    if length == 0:
        raise Exception("Insufficient arguments were provided")
    elif length > 1:
        raise Exception("Extra arguments were provided")
    symbols = args[0].split(',')
    # Get the historical price
    tokens_prices = get_historical_price(symbols)
    
    # Retrieve the last 6 values, corresponding to last half hour if tf is 5min.
    result = []
    for token_prices in tokens_prices:
        # Calculate median prices
        result.append(median(token_prices))

    # Return median prices
    return ",".join(map(str, result))

if __name__ == "__main__":
    try:
        print(main(sys.argv[1:]))
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)
