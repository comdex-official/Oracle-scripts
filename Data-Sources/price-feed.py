#!/usr/bin/env python3
from unittest import result
import requests
import json
import sys

CONSTANTS = {
    "OSMOSIS" : {
        "SYMBOLS": {},
        "URL": "https://api-osmosis.imperator.co/tokens/v2/all"
    },
    "COIN_GECKO" : {
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
            "MED" : "medibloc",
            "CHEQ": "cheqd-network",
            "STARS": "stargaze",
            "HUAHUA": "chihuahua-token",
            "LUM"  : "lum-network",
            "VDL"  : "vidulum",
            "DSM"  : "desmos",
        },
        "URL" : "https://api.coingecko.com/api/v3/simple/price?ids={COMMA_SEPRATED_IDS}&vs_currencies=USD"
    },
}

def getPriceFromCoinGecko(symbols):
    if not symbols:
        return []
    
    symbolsLen = len(symbols)
    valid_coin_gecko_ids = []
    for symbol in symbols:
        if CONSTANTS["COIN_GECKO"]["SYMBOLS"].get(symbol):
            valid_coin_gecko_ids.append(CONSTANTS["COIN_GECKO"]["SYMBOLS"][symbol])
    
    if not valid_coin_gecko_ids:
        return [0 for i in range(symbolsLen)]

    result = []
    url = CONSTANTS["COIN_GECKO"]["URL"].format(COMMA_SEPRATED_IDS=",".join(valid_coin_gecko_ids))
    try:
        resp = requests.get(url)
        if resp.status_code != 200:
            return [0 for i in range(symbolsLen)]
        resp = resp.json()
        for symbol in symbols:
            if CONSTANTS["COIN_GECKO"]["SYMBOLS"].get(symbol):
                if resp.get(CONSTANTS["COIN_GECKO"]["SYMBOLS"][symbol]):
                    result.append(resp[CONSTANTS["COIN_GECKO"]["SYMBOLS"][symbol]]["usd"])
                else:
                    result.append(0)
            else:
                result.append(0)
    except Exception as e:
        return [0 for i in range(symbolsLen)]
    return result

def getPriceFromOsmosis(symbols):
    if not symbols:
        return []

    symbolsLen = len(symbols)
    try:
        resp = requests.get(CONSTANTS["OSMOSIS"]["URL"])
        if resp.status_code == 200:
            allAssetsList = resp.json()
            symbolPriceMap = {}
            for asset in allAssetsList:
                # skipping prices of gravity bridge assets
                if ".grv" not in asset["symbol"]:
                    symbolPriceMap[asset["symbol"]] = round(asset["price"], 6)
            result = []
            for symbol in symbols:
                result.append(symbolPriceMap.get(symbol, 0))
            return result
        return [0 for i in range(symbolsLen)]
    except Exception as e:
        return [0 for i in range(symbolsLen)]

def get_cmst_price():
    URL = "https://testnet-stat.comdex.one/cmst/price"
    HEADER = {
        "Accept":"application/json",
        "User-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:105.0) Gecko/20100101 Firefox/105.0"
    }
    try:
        result = requests.get(URL, headers=HEADER).json()
        # print(result.text)
        return result['data']['cmst_price']
    except Exception as e:
        print(e)
        return 0.0

def main(symbols):
    # skipping prices from coin gecko because of rate limit
    # priceList = getPriceFromCoinGecko(symbols)
    cmst = None
    if "CMST" in symbols:
        cmst = symbols.index("CMST")
        symbols.pop(cmst)
        cmst_price = get_cmst_price()
    priceList = getPriceFromOsmosis(symbols)
    if cmst != None:
        priceList.insert(cmst, cmst_price)
    return ",".join(str(price) for price in priceList)

if __name__ == "__main__":
    try:
        print(main(sys.argv[1:]))
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)
