#!/usr/bin/env python3
import requests
import json
import sys
PRICE_URL = "https://min-api.cryptocompare.com/data/pricemulti"

def adjust_rounding(data):
    if data < 1:
        return round(data, 8)
    elif data < 10:
        return round(data, 6)
    else:
        return round(data, 4)


def main(symbols):
    COSMOS_TOKENS = {
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

    }
    COMMODITIES = {
        "XAU" : "gold",
        "XAG" : "silver",
        "OIL" : "oil",
    }
    slugs = []
    d = {}
    for symbol in symbols:
        if symbol not in COSMOS_TOKENS and symbol not in COMMODITIES:
            d[symbol]=0
        if symbol in COSMOS_TOKENS:    
            slugs.append(symbol)
        else:
            d[symbol] = 0

    prices = requests.get(
        PRICE_URL,
        params={"fsyms": ",".join(slugs), "tsyms": "USD"},
    ).json()
    
    for token,name in COSMOS_TOKENS.items():
        for (key, px) in list(prices.items()):
            if token == key:
                d[token]=px['USD']
    result=[]
    index=0
    for symbol in symbols:
        if symbol in d:
            result.insert(index,d[symbol])
        else:
            result.insert(index,0)
        index+=1
    return ",".join([str(adjust_rounding(px)) for px in result])


if __name__ == "__main__":
    try:
        print(main([*sys.argv[1:]]))
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)

