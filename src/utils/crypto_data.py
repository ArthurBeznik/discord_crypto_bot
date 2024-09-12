# crypto_data.py

import pandas as pd
import requests
import logging
import json
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)

CACHE_DIR = "data"
MAP_CACHE_FILE = os.path.join(CACHE_DIR, "crypto_map.json")
LIST_CACHE_FILE = os.path.join(CACHE_DIR, "crypto_list.json")
CACHE_DURATION = timedelta(days=1) # Cache duration

API_URL = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page=1"

def fetch_from_cache_or_api(cache_file, fetch_function):
    """
    Fetch data from cache if valid, otherwise fetch from API and cache it.

    Args:
        cache_file (str): Path to the cache file.
        fetch_function (callable): Function to fetch data from the API.

    Returns:
        dict: Data loaded from cache or fetched from the API.
    """
    if os.path.exists(cache_file):
        file_mod_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
        if datetime.now() - file_mod_time < CACHE_DURATION:
            logger.info(f"Loading data from cache: {cache_file}")
            with open(cache_file, 'r') as f:
                return json.load(f)
    
    logger.info(f"Fetching data from API: {cache_file}")
    data = fetch_function()
    if data:
        with open(cache_file, 'w') as f:
            json.dump(data, f)
        logger.info(f"Cached {len(data)} items.")
    else:
        logger.error(f"Failed to fetch data for {cache_file}.")
    
    return data

def load_crypto_map() -> dict | None:
    """_summary_

    Returns:
        dict | None: _description_
    """
    def fetch_crypto_map():
        response = requests.get(API_URL)
        if response.status_code == 200:
            cryptos = response.json()
            crypto_map = {}
            for crypto in cryptos:
                crypto_map[crypto['id']] = crypto['id']
                crypto_map[crypto['name'].lower()] = crypto['id']
                crypto_map[crypto['symbol'].lower()] = crypto['id']
            return crypto_map
        return None

    return fetch_from_cache_or_api(MAP_CACHE_FILE, fetch_crypto_map)

def load_crypto_list() -> list[dict] | None:
    """_summary_

    Returns:
        list[dict] | None: _description_
    """
    def fetch_crypto_list():
        response = requests.get(API_URL)
        if response.status_code == 200:
            cryptos = response.json()
            return [{'id': crypto['id'], 'symbol': crypto['symbol'], 'name': crypto['name']} for crypto in cryptos]
        return None

    return fetch_from_cache_or_api(LIST_CACHE_FILE, fetch_crypto_list)

def fetch_crypto_data(crypto_id: str, days: int = 30):
    """
    Fetch historical market data for a cryptocurrency.

    Args:
        crypto_id (str): Cryptocurrency ID.
        days (int): Number of days of historical data to fetch.

    Returns:
        pd.DataFrame: DataFrame with historical prices and volumes.
    """
    url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart?vs_currency=usd&days={days}"
    response = requests.get(url)
    data = response.json()

    if "prices" not in data or "total_volumes" not in data:
        return None

    # Convert price and volume data to DataFrames
    price_df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
    price_df['timestamp'] = pd.to_datetime(price_df['timestamp'], unit='ms')
    price_df.set_index('timestamp', inplace=True)

    volume_df = pd.DataFrame(data['total_volumes'], columns=['timestamp', 'volume'])
    volume_df['timestamp'] = pd.to_datetime(volume_df['timestamp'], unit='ms')
    volume_df.set_index('timestamp', inplace=True)

    # Merge DataFrames
    price_df['volume'] = volume_df['volume']
    return price_df

def fetch_crypto_info(crypto_id: str):
    """
    Fetch detailed market data for a cryptocurrency.

    Args:
        crypto_id (str): Cryptocurrency ID.

    Returns:
        dict: Dictionary with detailed market data.
    """
    url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None
