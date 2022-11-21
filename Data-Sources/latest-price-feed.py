#!/usr/bin/env python3
from unittest import result
import requests
import json
import sys
from pprint import pprint

CONSTANTS = {
    "OSMOSIS": {
        "SYMBOLS": {},
        "URL": "https://api-osmosis.imperator.co/tokens/v2/all"
    },
    "COIN_GECKO": {
        "SYMBOLS": {
            "ATOM": "cosmos",
            "OSMO": "osmosis",
            "SCRT": "secret",
            "AKT": "akash-network",
            "UST": "terrausd",
            "JUNO": "juno-network",
            "CRO": "crypto-com-chain",
            "ION": "ion",
            "XPRT": "persistence",
            "DVPN": "sentinel",
            "LUNA": "terra-luna",
            "REGEN": "regen",
            "KRT": "terra-krw",
            "IRIS": "iris-network",
            "IOV": "starname",
            "NGM": "e-money",
            "IXO": "ixo",
            "BCNA": "bitcanna",
            "BTSG": "bitsong",
            "XKI": "ki",
            "LIKE": "likecoin",
            "EEUR": "e-money-eur",
            "BAND": "band-protocol",
            "CMDX": "comdex",
            "TICK": "microtick",
            "MED": "medibloc",
            "CHEQ": "cheqd-network",
            "STARS": "stargaze",
            "HUAHUA": "chihuahua-token",
            "LUM": "lum-network",
            "VDL": "vidulum",
            "DSM": "desmos",
            "BTC": "bitcoin",
            "WBTC": "wrapped-bitcoin",
            "ETH": "ethereum",
            "WETH": "weth",
            "USDC": "usd-coin",
            "DAI": "dai",
        },
        "URL": "https://api.coingecko.com/api/v3/simple/price"
    },
}


def get_price_coingecko(symbols):
    # Set a header for api
    HEADER = {
        "Accept": "application/json",
    }

    # Get ids for supplied symbols
    coin_ids = {symbol: CONSTANTS["COIN_GECKO"]
                ["SYMBOLS"].get(symbol, symbol) for symbol in symbols}

    PARAMETERS = {
        "ids": ",".join(coin_ids.values()),
        "vs_currencies": "usd",
        "precision": "full",
    }

    result = []
    url = CONSTANTS["COIN_GECKO"]["URL"]
    try:
        # Make api call
        response = requests.get(url, params=PARAMETERS, headers=HEADER).json()
        # Retrieve prices from response
        for symbol in symbols:
            coin_id = coin_ids.get(symbol, None)
            result.append(response[coin_id]["usd"] if coin_id else 0.0)
        # Return prices
        return result
    except Exception as e:
        return [0.0]*len(symbols)


def get_price_osmosis(symbols):
    # URL to retrieve the price of all tokens
    URL = "https://api-osmosis.imperator.co/tokens/v2/all"
    HEADER = {
        "Accept": "application/json"
    }
    # Request prices of all tokens from API and retrieve the prices for
    # requested tokens. Return 0, if the request fails.
    prices = {}
    try:
        response = requests.get(URL, headers=HEADER).json()
        for item in response:
            prices[item["symbol"]] = item["price"]
        result = [prices.get(symbol, 0.0) for symbol in symbols]
        return result
    except Exception as e:
        return [0.0]*len(symbols)


def get_cmst_price():
    URL = "https://testnet-stat.comdex.one/cmst/price"
    HEADER = {
        "Accept": "application/json",
        "User-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:105.0) Gecko/20100101 Firefox/105.0"
    }
    try:
        result = requests.get(URL, headers=HEADER).json()
        return result['data']['cmst_price']
    except Exception as e:
        return 0.0


def get_harbor_price():
    URL = "https://testnet-stat.comdex.one/cswap/prices"
    HEADER = {
        "Accept": "application/json",
        "User-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:105.0) Gecko/20100101 Firefox/105.0"
    }
    try:
        result = requests.get(URL, headers=HEADER).json()
        return result["data"]['ucmst']["uharbor"]['price']
    except Exception as e:
        return 0.0


def main(symbols):
    if len(symbols) == 0:
        return ""

    try:
        # Get CMST price
        cmst_index = None
        if "CMST" in symbols:
            cmst_index = symbols.index("CMST")
            symbols.pop(cmst_index)
            cmst_price = get_cmst_price()

        # Get HARBOR price
        harbor_index = None
        if "HARBOR" in symbols:
            harbor_index = symbols.index("HARBOR")
            symbols.pop(harbor_index)
            harbor_price = get_harbor_price()

        # Get price from coin gecko
        result_coingecko = get_price_coingecko(symbols)
        # Get price from osmosis
        result_osmosis = get_price_osmosis(symbols)

        result = []
        for item in zip(result_coingecko, result_osmosis):
            if item[0] == 0 and item[1] != 0:
                result.append(item[1])
            elif item[0] != 0 and item[1] == 0:
                result.append(item[0])
            else:
                result.append(sum(item)/2)

        # Insert cmst price in same order as requested symbols
        if harbor_index is not None:
            result.insert(harbor_index, harbor_price)
        if cmst_index is not None:
            result.insert(cmst_index, cmst_price)
        return ",".join(str(price) for price in result)
    except Exception:
        return [0.0]*len(symbols)


if __name__ == "__main__":
    try:
        print(main(sys.argv[1:]))
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)
