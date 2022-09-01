#!/usr/bin/env python3
import requests
import sys
import json

def get_price_osmosis(symbols):
    symbols = symbols.split(",")
    # URL to retrieve the price of all tokens
    URL = "https://api-osmosis.imperator.co/tokens/v2/all"
    HEADER = {
        "Accept": "application/json"
    }
    # Request prices of all tokens from API and extract the prices for the
    # requested symbols.
    prices = {}
    for item in requests.get(URL, headers=HEADER).json():
        # If the item symbol is one of requested, then store the result
        if item["symbol"] in symbols:
            prices[item["symbol"]] = item["price"]
    return [prices[symbol] for symbol in symbols]

def get_price_coinmarket(symbols):
    # URL to retrieve the ID of each token
    URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/map"
    HEADER = {
        "Accept": "application/json",
        "X-CMC_PRO_API_KEY": "83ae2f96-8f84-4dc7-9422-5ea5fb065195"
    }
    parameters = {"symbol":symbols}
    # Request ID from API
    id_map = requests.get(URL, headers=HEADER, params=parameters)
    if id_map.status_code != 200:
        raise Exception("Failed to get price from CoinMarketCap")
    # Retrieve IDs
    with open("coinmarketcap.json", "w+") as fp:
        json.dump(id_map.json(), fp=fp)
    ids = [str(item["id"]) for item in id_map.json()["data"]]

    # Request price from API
    URL = "https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest"
    parameters = {"id":",".join(ids), "convert":"USD"}
    prices = requests.get(URL, headers=HEADER, params=parameters)
    # Retrieve price
    with open("coinmarketcap.json", "w+") as fp:
        json.dump(prices.json()["data"], fp)
    return [value["quote"]["USD"]["price"] for _,value in prices.json()["data"].items()]

def main(args):
    length = len(args)
    if length == 0:
        raise Exception("Insufficient arguments were provided")
    elif length > 1:
        raise Exception("Extra arguments were provided")
    # Get the historical price
    
    result = get_price_osmosis(args[0])
    

    # Return median prices
    return ",".join(map(str, result))

if __name__ == "__main__":
    try:
        print(main(sys.argv[1:]))
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)
