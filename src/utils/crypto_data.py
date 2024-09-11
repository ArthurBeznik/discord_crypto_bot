import pandas as pd
import requests
import logging
import json
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)
crypto_map = {}

def fetch_crypto_data(crypto_id: str, days: int = 30):
    """_summary_

    Args:
        crypto_id (str): _description_
        days (int, optional): _description_. Defaults to 30.

    Returns:
        _type_: _description_
    """
    url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart?vs_currency=usd&days={days}"
    response = requests.get(url)
    data = response.json()

    if "prices" not in data or "total_volumes" not in data:
        return None

    # Convert price data to DataFrame
    df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)

    # Convert volume data to DataFrame
    volume_df = pd.DataFrame(data['total_volumes'], columns=['timestamp', 'volume'])
    volume_df['timestamp'] = pd.to_datetime(volume_df['timestamp'], unit='ms')
    volume_df.set_index('timestamp', inplace=True)

    # Merge the two DataFrames
    df['volume'] = volume_df['volume']

    return df

CACHE_FILE = "data/crypto_list.json"
CACHE_DURATION = timedelta(days=1)  # Cache the list for 1 day

def load_crypto_list():
    """
    Load the cryptocurrency list from a cache file if it exists and is valid.
    Otherwise, fetch it from the CoinGecko API and store it in a cache file.
    """
    # Check if the cache file exists and if it's still valid (not expired)
    if os.path.exists(CACHE_FILE):
        file_mod_time = datetime.fromtimestamp(os.path.getmtime(CACHE_FILE))
        if datetime.now() - file_mod_time < CACHE_DURATION:
            logger.info("Loading cryptocurrency list from cache.")
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
    
    # If no valid cache, fetch the list from the API
    logger.info("Fetching cryptocurrency list from CoinGecko API...")
    url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250=&page=1"
    response = requests.get(url)
    
    if response.status_code == 200:
        cryptos = response.json()
        for crypto in cryptos:
            crypto_map[crypto['id']] = crypto['id']
            crypto_map[crypto['name'].lower()] = crypto['id']
            crypto_map[crypto['symbol'].lower()] = crypto['id']

        # Cache the data to the file
        with open(CACHE_FILE, 'w') as f:
            json.dump(crypto_map, f)

        logger.info(f"Loaded and cached {len(cryptos)} cryptocurrencies.")
    else:
        logger.error(f"Failed to load cryptocurrencies. Status code: {response.status_code}")
    
    return crypto_map
