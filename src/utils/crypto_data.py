# crypto_data.py

from typing import Dict, List
import pandas as pd
import requests
import json
from datetime import datetime
import os

from utils.config import (
    MAP_CACHE_FILE,
    LIST_CACHE_FILE,
    CACHE_DURATION,
    CG_API_URL,
)
from utils.logger import logging


logger = logging.getLogger(__name__)


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
            with open(cache_file, "r") as f:
                return json.load(f)

    logger.info(f"Fetching data from API into {cache_file}")
    data = fetch_function()

    logger.debug(f"data: {data}")  # ? debug

    if data:
        with open(cache_file, "w") as f:
            json.dump(data, f)
        logger.info(f"Cached {len(data)} items")
        return data
    else:
        logger.error(f"Failed to fetch data for {cache_file}")
        return None


def load_crypto_map() -> dict | None:
    """Loads a cryptocurrency map from an API or cache, skipping duplicates.

    Returns:
        dict | None: _description_
    """

    def fetch_crypto_map():
        url = CG_API_URL
        response = requests.get(url)
        if response.status_code == 200:
            cryptos: List[Dict[str, str]] = response.json()

            logger.debug(f"cryptos: {cryptos}")  # ? debug

            crypto_map: dict[str, str] = {}
            for crypto in cryptos:
                # logger.debug(f"crypto: {crypto}")  # ? debug

                crypto_id = crypto["id"]
                crypto_name = crypto["name"].lower()
                crypto_symbol = crypto["symbol"].lower()

                logger.debug(
                    f"crypto_id: {crypto_id} | crypto_name: {crypto_name} | crypto_symbol: {crypto_symbol}"
                )  # ? debug

                if (crypto_id and crypto_name and crypto_symbol) not in crypto_map:
                    crypto_map[crypto_name] = crypto_id
                    crypto_map[crypto_symbol] = crypto_id
                    crypto_map[crypto_id] = crypto_id

                    logger.debug(
                        f"Added to crypto_map: {crypto_id} ({crypto_symbol})"
                    )  # ? debug

                else:
                    logger.warning(
                        f"Crypto already set in crypto_map: {crypto_id} | {crypto_name} | {crypto_symbol}"
                    )

                # logger.debug(f"crypto_map: {crypto_map}") #? debug

            logger.debug(f"Final crypto_map: {crypto_map}")  # ? debug
            return crypto_map
        else:
            logger.error(
                f"Failed to fetch crypto_map. Status code: {response.status_code}"
            )
            return None

    return fetch_from_cache_or_api(MAP_CACHE_FILE, fetch_crypto_map)


def load_crypto_list() -> list[dict] | None:
    """_summary_

    Returns:
        list[dict] | None: _description_
    """

    def fetch_crypto_list():
        url = CG_API_URL
        response = requests.get(url)
        if response.status_code == 200:
            cryptos = response.json()
            return [
                {"id": crypto["id"], "symbol": crypto["symbol"], "name": crypto["name"]}
                for crypto in cryptos
            ]
        else:
            logger.error(
                f"Failed to fetch crypto_list. Status code: {response.status_code}"
            )
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
    logger.info(f"crypto_id: {crypto_id} | days: {days}")  # ? debug

    url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart?vs_currency=usd&days={days}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        if "prices" not in data or "total_volumes" not in data:
            return None

        # Convert price and volume data to DataFrames
        price_df = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
        price_df["timestamp"] = pd.to_datetime(price_df["timestamp"], unit="ms")
        price_df.set_index("timestamp", inplace=True)

        volume_df = pd.DataFrame(data["total_volumes"], columns=["timestamp", "volume"])
        volume_df["timestamp"] = pd.to_datetime(volume_df["timestamp"], unit="ms")
        volume_df.set_index("timestamp", inplace=True)

        # Merge DataFrames
        price_df["volume"] = volume_df["volume"]
        return price_df
    else:
        logger.error(
            f"Failed to fetch data for {crypto_id} | days: {days}. Status code: {response.status_code}"
        )
        return None


def fetch_crypto_info(crypto_id: str):
    """
    Fetch detailed market data for a cryptocurrency.

    Args:
        crypto_id (str): Cryptocurrency ID.

    Returns:
        dict: Dictionary with detailed market data.
    """
    logger.info(f"Fetching info for crypto: {crypto_id}")

    url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}"
    response = requests.get(url)
    if response.status_code == 200:
        logger.info(f"Fetched crypto info successfully for: {crypto_id}")
        return response.json()
    else:
        logger.error(f"Failed to fetch crypto info for: {crypto_id}")
        return None
