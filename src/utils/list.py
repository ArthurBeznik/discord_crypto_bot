import discord
import requests
import logging

logger = logging.getLogger(__name__)

crypto_map = {}

def load_crypto_list():
    """
    Fetch the list of cryptocurrencies from the CoinGecko API 
    and return a dictionary mapping name and symbol to id.
    """
    # logger.info("Loading cryptocurrency list from CoinGecko API...")

    url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250=&page=1"
    response = requests.get(url)
    
    if response.status_code == 200:
        cryptos = response.json()
        for crypto in cryptos:
            crypto_map[crypto['id']] = crypto['id']
            crypto_map[crypto['name'].lower()] = crypto['id']
            crypto_map[crypto['symbol'].lower()] = crypto['id']
        logger.info(f"Loaded {len(cryptos)} cryptocurrencies.")
        # logger.info(f"Data: {cryptos}") # ? debug
    else:
        logger.error(f"Failed to load cryptocurrencies. Status code: {response.status_code}")
    
    return crypto_map

async def get_crypto_autocomplete_choices(interaction: discord.Interaction, input_value: str):
    """
    Return a list of autocomplete choices based on the last word in the input.
    """
    # logger.info(f"input_value: {input_value}") # ? debug

    if not input_value.strip():
        return []

    # Split the input by spaces, autocomplete only for the last part
    last_input = input_value.split()[-1]
    
    # Search for matches for the last word in the crypto_map
    choices = [discord.app_commands.Choice(name=key, value=key)
               for key in crypto_map if last_input.lower() in key.lower()]
    
    # Return a maximum of 25 autocomplete choices
    return choices[:25]
