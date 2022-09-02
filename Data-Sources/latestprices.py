#!/usr/bin/env python3
import requests
import sys
import json

def get_price_osmosis(symbols):
    print("Getting price from Osmosis..")
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
    print("Getting price from CoinMarketCap..")
    symbols = symbols.split(",")
    if "ATOM" in symbols:
        atom = True
    # URL to retrieve the ID of each token
    URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/map"
    HEADER = {
        "Accept": "application/json",
        "X-CMC_PRO_API_KEY": "83ae2f96-8f84-4dc7-9422-5ea5fb065195"
    }
    if atom:
        symbols.remove("ATOM")
    parameters = {"symbol":",".join(symbols)}
    # Request ID from API
    id_map = requests.get(URL, headers=HEADER, params=parameters)
    if id_map.status_code != 200:
        raise Exception("Failed to get price from CoinMarketCap", id_map.status_code, id_map.reason)
    # Retrieve IDs
    ids = [str(item["id"]) for item in id_map.json()["data"]]
    if atom:
        ids.append("3794")
        symbols.append("ATOM")

    # Request price from API
    URL = "https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest"
    parameters = {"id":",".join(ids), "convert":"USD"}
    result = requests.get(URL, headers=HEADER, params=parameters)
    # Retrieve price
    # prices =  [value["quote"]["USD"]["price"] for _,value in result.json()["data"].items()]
    prices = {}
    for key, value in result.json()["data"].items():
        prices[value["symbol"]] = value["quote"]["USD"]["price"]
    return [prices[symbol] for symbol in symbols]

def get_price_coingecko(symbols):
    print("Getting price from CoinGecko..")
    lc_symbols = list(map(lambda x: x.lower(), symbols.split(",")))
    # Retrieve the symbol id mappings
    URL = "https://api.coingecko.com/api/v3/coins/list?include_platform=false"
    HEADER = {
        "Accept": "application/json"
    }
    result = requests.get(URL, headers=HEADER)
    ids = {}
    for item in result.json():
        if item["symbol"] in lc_symbols:
            ids[item["symbol"]] = item["id"]

    # Retrieve the prices for symbols
    URL = "https://api.coingecko.com/api/v3/simple/price"
    parameters = {
        "ids":",".join(ids.values()),
        "vs_currencies":"usd"
    }
    result = requests.get(URL, params=parameters, headers=HEADER).json()
    prices = {}
    for symbol in lc_symbols:
        id = ids.get(symbol, None)
        if id:
            prices[symbol] = result[id]["usd"]
        else:
            prices[symbol] = 0
    return [prices[symbol] for symbol in lc_symbols]

def main(args):
    length = len(args)
    if length == 0:
        raise Exception("Insufficient arguments were provided")
    elif length > 1:
        raise Exception("Extra arguments were provided")
    
    result_coinmarket = get_price_coinmarket(args[0])
    result_osmosis = get_price_osmosis(args[0])
    result_coingecko = get_price_coingecko(args[0])

    result = []
    for item in zip(result_osmosis, result_coinmarket, result_coingecko):
        result.append(",".join(map(str, item)))
        # print(item)
    
    return "\n".join(result)

if __name__ == "__main__":
    print(main(sys.argv[1:]))
    # try:
    #     print(main(sys.argv[1:]))
    # except Exception as e:
    #     print(e, file=sys.stderr)
    #     sys.exit(1)
