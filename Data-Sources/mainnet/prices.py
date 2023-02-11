#!/usr/bin/env python3
from unittest import result
import requests
import json
import sys

CONSTANTS = {
    "OSMOSIS": {
        "SYMBOLS": {
            "ATOM": "ATOM",
            "OSMO": "OSMO",
            "SCRT": "SCRT",
            "AKT": "AKT",
            "JUNO": "JUNO",
            "CRO": "CRO",
            "ION": "ION",
            "XPRT": "XPRT",
            "DVPN": "DVPN",
            "REGEN": "REGEN",
            "NGM": "NGM",
            "EEUR": "EEUR",
            "BAND": "BAND",
            "CMDX": "CMDX",
            "STARS": "STARS",
            "HUAHUA": "HUAHUA",
            "DSM": "DSM",
            "AXLWBTC": "WBTC",
            "WETH": "WETH",
            "AXLUSDC": "USDC",
            "AXLUSDT": "USDT",
            "AXLDAI": "DAI",
            "GWETH": "WETH.grv",
            "GUSDC": "USDC.grv",
            "GUSDT": "USDT.grv",
            "WMATIC": "WMATIC",
            "AXLWBNB": "WBNB",
            "EVMOS": "EVMOS",
            "STATOM": "stATOM",
            "STOSMO": "stOSMO",
            "LUNA": "LUNA",
        },
        "URL": "https://api-osmosis.imperator.co/tokens/v2/all"
    },
    "COIN_GECKO": {
        "SYMBOLS": {
            "ATOM": "cosmos",
            "OSMO": "osmosis",
            "SCRT": "secret",
            "AKT": "akash-network",
            "JUNO": "juno-network",
            "CRO": "crypto-com-chain",
            "ION": "ion",
            "XPRT": "persistence",
            "DVPN": "sentinel",
            "REGEN": "regen",
            "NGM": "e-money",
            "EEUR": "e-money-eur",
            "BAND": "band-protocol",
            "CMDX": "comdex",
            "STARS": "stargaze",
            "HUAHUA": "chihuahua-token",
            "DSM": "desmos",
            "AXLWBTC": "axlwbtc",
            "WETH": "axlweth",
            "AXLUSDC": "axlusdc",
            "AXLDAI": "dai",
            "GWBTC": "gravity-bridge-wbtc",
            "GWETH": "gravity-bridge-weth",
            "GUSDC": "gravity-bridge-usdc",
            "GUSDT": "gravity-bridge-tether",
            "GDAI": "gravity-bridge-dai",
            "WMATIC": "wmatic",
            "AXLWBNB": "wbnb",
            "EVMOS": "evmos",
            "STATOM": "stride-staked-atom",
            "STOSMO": "stride-staked-osmo",
            "LUNA": "terra-luna-2",
            "CANTO": "canto",
        },
        "URL": "https://api.coingecko.com/api/v3/simple/price"
    },
}


def get_price_coingecko(symbols):
    # Return empty response if no symbols
    if not symbols:
        return []

    # Get ids for supplied symbols
    coin_ids_map = {symbol: CONSTANTS["COIN_GECKO"]["SYMBOLS"].get(
        symbol, "") for symbol in symbols}

    # Set a header for api
    HEADER = {
        "Accept": "application/json",
    }

    # Set request parameters
    PARAMETERS = {
        "ids": ",".join(coin_ids_map.values()),
        "vs_currencies": "usd",
        "precision": "full",
    }

    # URL to retrieve the price of all tokens
    url = CONSTANTS["COIN_GECKO"]["URL"]

    result = []
    try:
        # Make api call
        response = requests.get(url, params=PARAMETERS, headers=HEADER).json()

        # Retrieve prices from response
        for symbol in symbols:
            coin_id = coin_ids_map.get(symbol, None)
            result.append(response[coin_id]["usd"] if coin_id else 0)

        # Return prices
        return result
    except Exception as e:
        return [0 for i in range(len(symbols))]


def get_price_osmosis(symbols):
    # Return empty response if no symbols
    if not symbols:
        return []

    # Set a header for api
    HEADER = {
        "Accept": "application/json"
    }

    # URL to retrieve the price of all tokens
    url = CONSTANTS["OSMOSIS"]["URL"]

    # Request prices of all tokens from API and retrieve the prices for
    # requested tokens. Return 0, if the request fails.
    try:
        response = requests.get(url, headers=HEADER).json()

        osmosis_symbol_prices_map = {}
        for token in response:
            osmosis_symbol_prices_map[token["symbol"]] = token["price"]

        return [osmosis_symbol_prices_map[CONSTANTS["OSMOSIS"]["SYMBOLS"][symbol]] if CONSTANTS["OSMOSIS"]["SYMBOLS"].get(symbol, None) else 0 for symbol in symbols]

    except Exception as e:
        return [0 for i in range(len(symbols))]


def get_price_cswap(symbol):
    URL = f"https://stat.comdex.one/api/v2/cswap/tokens/{symbol}"
    HEADER = {
        "Accept": "application/json",
        "User-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:105.0) Gecko/20100101 Firefox/105.0"
    }
    try:
        result = requests.get(URL, headers=HEADER).json()
        return result["data"]['price'] if isinstance(result["data"]['price'], float) else 0
    except Exception as e:
        return 0


def main(symbols):
    if len(symbols) == 0:
        return ""

    try:
        # Get CMST price
        cmst_index = None
        if "CMST" in symbols:
            cmst_index = symbols.index("CMST")
            symbols.pop(cmst_index)
            cmst_price = get_price_cswap("CMST")

        # Get HARBOR price
        harbor_index = None
        if "HARBOR" in symbols:
            harbor_index = symbols.index("HARBOR")
            symbols.pop(harbor_index)
            harbor_price = get_price_cswap("HARBOR")

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
        return ",".join("0" for i in range(len(symbols)))


if __name__ == "__main__":
    try:
        print(main(sys.argv[1:]))
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)
