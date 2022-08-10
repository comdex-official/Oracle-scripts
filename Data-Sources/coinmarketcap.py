#!/usr/bin/env python3
from requests import Request, Session
import json
import time
import webbrowser
import sys
import pprint


def adjust_rounding(data):
    if data < 1:
        return round(data, 8)
    elif data < 10:
        return round(data, 6)
    else:
        return round(data, 4)

url1 = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/map'
url2 = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'


def getInfo(symbol): 
    url1 = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/map'
    url2 = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    parameters1 = { 'symbol':symbol}
    parameters2 ={'start':'1','limit':'5000','convert': 'USD'}
    parameters3={'start':'5001','limit':'5000','convert': 'USD'}
    parameters4={}
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': '83ae2f96-8f84-4dc7-9422-5ea5fb065195'
    } 
    session = Session()
    session.headers.update(headers)

    response1 = session.get(url1, params=parameters1)
    response2 = session.get(url2,params=parameters2)
    info1=json.loads(response1.text)['data'][0]['id']
    info2=json.loads(response2.text)
    pprint.pprint(info1)
    for x in info2['data']:
        if x['id']==info1:
            pprint.pprint(x['quote']['USD']['price'])
            pprint.pprint(x)

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

getInfo('CMDX')

if __name__ == "__main__":
    try:
        print(main([*sys.argv[1:]]))
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)
