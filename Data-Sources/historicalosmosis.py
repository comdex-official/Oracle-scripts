import requests
import sys

# URL to fetch historical data for a specific token using osmosis api
URL = "https://api-osmosis.imperator.co/tokens/v2/historical/{}/chart"
# Allowed tf values in api
tf_vals = [5,15,30,60,120,240,720,1440,10080,43800]
# Num of vals to retrieve. 6 represents half hour for 5 min intervals.
NUM_VALS = 6

def get_historical_price(symbol, tf):
    if int(tf) not in tf_vals:
        raise Exception(f"Invalid value: {tf=}. Valid values: {tf_vals}")
    # Add symbol to URL
    url = URL.format(symbol)
    # Time frequency, eg 5(min).
    parameters = {"tf": tf}
    # Request data
    r = requests.get(url, params=parameters)
    if r.status_code != 200:
        raise Exception(f"Unable to fetch price. Provided args:{symbol=}, {tf=}.")
    return r.json()

def main(args):
    length = len(args)
    if length == 0:
        raise Exception("Insufficient arguments were provided.")
    elif length > 2:
        raise Exception("Extra arguments were provided.")
    
    # Get the historical price
    if length == 2:
        prices = get_historical_price(args[0], args[1])
    else:
        prices = get_historical_price(args[0], 5)
    
    # Retrieve the last 6 values, corresponding to last half hour if tf is 5min.
    result = []
    for price in prices[-6:]:
        result.append(round(price['close'], 6))

    # Return prices for the last half hour.
    return result

if __name__ == "__main__":
    try:
        print(main(sys.argv[1:]))
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)
