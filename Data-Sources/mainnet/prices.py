#!/usr/bin/env python3
from unittest import result
import requests
import json
import sys

STAT_URL = "https://stat.comdex.one"

CONSTANTS = {
    "OSMOSIS": {
        "SYMBOLS": {
            "ATOM": "ATOM", "OSMO": "OSMO", "SCRT": "SCRT", "AKT": "AKT", "JUNO": "JUNO", "CRO": "CRO", "ION": "ION", 
            "XPRT": "XPRT", "DVPN": "DVPN", "REGEN": "REGEN", "NGM": "NGM", "EEUR": "EEUR", "BAND": "BAND", "CMDX": "CMDX", 
            "STARS": "STARS", "HUAHUA": "HUAHUA", "DSM": "DSM", "AXLWBTC": "WBTC", "WETH": "WETH", "AXLUSDC": "USDC", 
            "AXLUSDT": "USDT", "AXLDAI": "DAI", "GWETH": "WETH.grv", "GUSDC": "USDC.grv", "GUSDT": "USDT.grv", "WMATIC": "WMATIC", 
            "AXLWBNB": "WBNB", "EVMOS": "EVMOS", "STATOM": "stATOM", "STOSMO": "stOSMO", "LUNA": "LUNA", "MNTL": "MNTL", "AXLWFTM": "WFTM",
            "CMST": "CMST", "AXLSHIB": "SHIB", "STKATOM": "STKATOM"
        },
        "URL": "https://api-osmosis.imperator.co/tokens/v2/all"
    },
    "COIN_GECKO": {
        "SYMBOLS": {
            "ATOM": "cosmos", "OSMO": "osmosis", "SCRT": "secret", "AKT": "akash-network", "JUNO": "juno-network", "CRO": "crypto-com-chain",
            "ION": "ion", "XPRT": "persistence", "DVPN": "sentinel", "REGEN": "regen", "NGM": "e-money", "EEUR": "e-money-eur", "BAND": "band-protocol",
            "CMDX": "comdex", "STARS": "stargaze", "HUAHUA": "chihuahua-token", "DSM": "desmos", "AXLWBTC": "axlwbtc", "WETH": "axlweth",
            "AXLUSDC": "axlusdc", "AXLDAI": "dai", "GWBTC": "gravity-bridge-wbtc", "GWETH": "gravity-bridge-weth", "GUSDC": "gravity-bridge-usdc",
            "GUSDT": "gravity-bridge-tether", "GDAI": "gravity-bridge-dai", "WMATIC": "wmatic", "AXLWBNB": "wbnb", "EVMOS": "evmos",
            "STATOM": "stride-staked-atom", "STOSMO": "stride-staked-osmo", "LUNA": "terra-luna-2", "CANTO": "canto", "MNTL": "assetmantle", "AXLWFTM": "wrapped-fantom",
            "CMST": "composite", "AXLSHIB": "shiba-inu", "STKATOM": "stkatom",
        },
        "URL": "https://api.coingecko.com/api/v3/simple/price"
    },
    "CSWAP": {
        "SYMBOLS": {
            "CMDX": "CMDX", "CMST": "CMST", "HARBOR": "HARBOR", "STJUNO": "STJUNO", "STLUNA": "STLUNA",
        },
        "URL": f"{STAT_URL}/api/v2/cswap/tokens/all"
    },
    "CRESCENT": {
        "SYMBOLS": {
            "ATOM": "ATOM", "AKT": "AKT", "JUNO": "JUNO", "CRO": "CRO", "CMDX": "CMDX", "WETH": "WETH.axl", "AXLUSDC": "USDC.axl", 
            "GWETH": "WETH.grv", "GUSDC": "USDC.grv", "GUSDT": "USDT.grv", "EVMOS": "EVMOS", "STATOM": "stATOM", "LUNA": "LUNA",
            "CMST": "CMST", "STKATOM": "stkATOM",
        },
        "URL": "https://apigw-v3.crescent.network/asset/live"
    },
    "COINDESK": {
        "SYMBOLS": {
            "ATOM": "ATOM", "OSMO": "OSMO", "SCRT": "SCRT","CRO": "CRO", "BAND": "BAND", "AXLWBTC": "WBTC", "LUNA": "LUNA",
        },
        "URL": "https://production.api.coindesk.com/v2/tb/price/ticker"
    },
}


def get_price_coingecko(symbols):
    # Return empty response if no symbols
    if not symbols:
        return []
    
    return [0 for i in range(len(symbols))] # Temp FIX, need to be removed later

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
        response = requests.get(url, params=PARAMETERS, headers=HEADER, timeout=3).json()

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
        response = requests.get(url, headers=HEADER, timeout=3).json()

        osmosis_symbol_prices_map = {}
        for token in response:
            osmosis_symbol_prices_map[token["symbol"]] = token["price"]

        return [osmosis_symbol_prices_map[CONSTANTS["OSMOSIS"]["SYMBOLS"][symbol]] if CONSTANTS["OSMOSIS"]["SYMBOLS"].get(symbol, None) else 0 for symbol in symbols]

    except Exception as e:
        return [0 for i in range(len(symbols))]


def get_price_cswap(symbols):
    # Return empty response if no symbols
    if not symbols:
        return []
    
    # Set a header for api
    HEADER = {
        "Accept": "application/json",
        "User-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:105.0) Gecko/20100101 Firefox/105.0"
    }

    # URL to retrieve the price of all tokens
    url = CONSTANTS["CSWAP"]["URL"]

    # Request prices of all tokens from API and retrieve the prices for
    # requested tokens. Return 0, if the request fails.
    try:
        response = requests.get(url, headers=HEADER, timeout=3).json()
        
        # return all prices as 0 if API fails or returns error
        if response.get("error"):
            return [0 for i in range(len(symbols))]
        
        cswap_symbol_prices_map = {}
        for token in response["data"]:
            cswap_symbol_prices_map[token["symbol"]] = token["price"]

        return [cswap_symbol_prices_map[CONSTANTS["CSWAP"]["SYMBOLS"][symbol]] if CONSTANTS["CSWAP"]["SYMBOLS"].get(symbol, None) else 0  for symbol in symbols]
    
    except Exception as e:
        return [0 for i in range(len(symbols))]


def get_price_crescent(symbols):
    if not symbols:
        return []
    
    HEADER = {
        "Accept": "application/json",
    }
    
    try:
        asset_info_response = requests.get("https://apigw-v3.crescent.network/asset/info", headers=HEADER, timeout=3).json()
        denom_symbol_map = {}
        for asset_info in asset_info_response["data"]:
            denom_symbol_map[asset_info["denom"]] = asset_info["ticker"]

        price_response = requests.get(CONSTANTS["CRESCENT"]["URL"], headers=HEADER, timeout=3).json()
        denom_price_map = {}
        for price in price_response["data"]:
            denom_price_map[price["denom"]] = price["priceOracle"]
        
        crescent_symbol_price_map = {}
        for denom, price in denom_price_map.items():
            if denom_symbol_map.get(denom):
                crescent_symbol_price_map[denom_symbol_map[denom]] = price

        return [crescent_symbol_price_map[CONSTANTS["CRESCENT"]["SYMBOLS"][symbol]] if CONSTANTS["CRESCENT"]["SYMBOLS"].get(symbol, None) else 0 for symbol in symbols]

    except Exception as e:
        return [0 for i in range(len(symbols))]
    

def get_price_coindesk(symbols):
    if not symbols:
        return []
    
    # Get ids for supplied symbols
    coin_ids_map = {}
    for symbol in symbols:
        if  CONSTANTS["COINDESK"]["SYMBOLS"].get(symbol):
            coin_ids_map[symbol] =  CONSTANTS["COINDESK"]["SYMBOLS"][symbol]
        else:
            pass

    # Set a header for api
    HEADER = {
        "Accept": "application/json",
    }

    # Set request parameters
    PARAMETERS = {
        "assets": ",".join(coin_ids_map.values()),
    }

    # URL to retrieve the price of all tokens
    url = CONSTANTS["COINDESK"]["URL"]

    result = []
    try:
        # Make api call
        response = requests.get(url, params=PARAMETERS, headers=HEADER, timeout=3).json()

        # Retrieve prices from response
        for symbol in symbols:
            coin_id = coin_ids_map.get(symbol, None)
            result.append(response["data"][coin_id]["ohlc"]["c"] if coin_id and response["data"].get(coin_id) else 0)

        # Return prices
        return result
    except Exception as e:
        return [0 for i in range(len(symbols))]

def main(symbols):
    if len(symbols) == 0:
        return ""

    try:
        # Get price from coin gecko
        result_coingecko = get_price_coingecko(symbols)

        # Get price from osmosis
        result_osmosis = get_price_osmosis(symbols)

        # Get price from cswap
        result_cswap = get_price_cswap(symbols)

        # Get price from crescent
        result_crescent = get_price_crescent(symbols)

        # Get price from coindesk
        result_coindesk = get_price_coindesk(symbols)

        # if lenghth of the results from all the sources is not same, then return 0
        if not len(result_coingecko) == len(result_osmosis) == len(result_cswap) == len(result_crescent) == len(result_coindesk):
            return ",".join("0" for i in range(len(symbols)))

        result = []
        for item in zip(result_coingecko, result_osmosis, result_cswap, result_crescent, result_coindesk):
            different_sources_price = list(item)
            non_zero_sources = [price for price in different_sources_price if price != 0]
            if non_zero_sources:
                mean = sum(non_zero_sources) / len(non_zero_sources)
                result.append(mean)
            else:
                result.append(0)

        return ",".join(str(price) for price in result)
    except Exception as e:
        return ",".join("0" for i in range(len(symbols)))

if __name__ == "__main__":
    try:
        print(main(sys.argv[1:]))
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)
