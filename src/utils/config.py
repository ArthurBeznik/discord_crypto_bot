# config.py

import os
from dotenv import load_dotenv
from datetime import timedelta
import discord

# ########################################################################################
# Paths
# ########################################################################################
DATA_PATH = "data"
LOGS_PATH = "logs"

os.makedirs(DATA_PATH, exist_ok=True)
os.makedirs(LOGS_PATH, exist_ok=True)

TUTORIALS_FILE = os.path.join(DATA_PATH, "tutorials.txt")
MAP_CACHE_FILE = os.path.join(DATA_PATH, "crypto_map.json")
LIST_CACHE_FILE = os.path.join(DATA_PATH, "crypto_list.json")
LOGS_FILE = os.path.join(LOGS_PATH, "bot.log")
CACHE_DURATION = timedelta(days=1)

# ########################################################################################
# Environment variables
# ########################################################################################
load_dotenv()

# Discord
DISCORD_BOT_TOKEN: str = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_GUILD_ID: str = os.getenv("DISCORD_GUILD_ID")
DISCORD_GUILD_OBJ: discord.Object = discord.Object(id=DISCORD_GUILD_ID)
ASK_CHAT_CHANNEL_ID: int = int(os.getenv("ASK_CHAT_CHANNEL_ID"))
TRADE_CHANNEL_ID: int = int(os.getenv("TRADE_CHANNEL_ID"))

# Database
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# APIs
## ChatGPT
CHATGPT_API_KEY: str = os.getenv("CHATGPT_API_KEY")

## CoinGecko - used for fetching prices
CG_API_KEY = os.getenv("")  # TODO
CG_API_URL = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page=1"

## NewsAPI - used to get the latest news
NEWS_API_KEY: str = os.getenv("NEWS_API_KEY")
NEWS_API_URL = "https://newsapi.org/v2/everything"

## Alternative - used for fear and greed indexes
ALT_API_URL = "https://api.alternative.me/fng/"

## Calendar - used for fetching events => FIND API
CALENDAR_API_KEY: str = os.getenv("CALENDAR_API_KEY")

# ########################################################################################
# Misc
# ########################################################################################
# Alert task loop
LOOP_MINUTES = 10

# Graphs
TIME_PERIOD = "Time period (e.g. 1d, 1w, 1m, 3m, 6m, or 1y)"
PERIOD_MAP = {
    "1d": "1",
    "1w": "7",
    "1m": "30",
    "3m": "90",
    "6m": "180",
    "1y": "365",
}

