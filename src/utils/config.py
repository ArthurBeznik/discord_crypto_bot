# config.py

import os
import logging
from dotenv import load_dotenv
from datetime import timedelta
import discord

# ########################################################################################
# Paths
# ########################################################################################
DATA_PATH = "data"
TUTORIALS_FILE = os.path.join(DATA_PATH, "tutorials.txt")
MAP_CACHE_FILE = os.path.join(DATA_PATH, "crypto_map.json")
LIST_CACHE_FILE = os.path.join(DATA_PATH, "crypto_list.json")
CACHE_DURATION = timedelta(days=1)

# ########################################################################################
# Environment variables
# ########################################################################################
load_dotenv()

# Discord
DISCORD_BOT_TOKEN: str = os.getenv('DISCORD_BOT_TOKEN')
DISCORD_GUILD_ID: str = os.getenv('DISCORD_GUILD_ID')
DISCORD_GUILD_OBJ: discord.Object = discord.Object(id=DISCORD_GUILD_ID)
ASK_CHAT_CHANNEL_ID: int = int(os.getenv('ASK_CHAT_CHANNEL_ID'))

# Database
DATABASE_URL = os.getenv('DATABASE_URL')

# APIs
## ChatGPT
CHATGPT_API_KEY: str = os.getenv('CHATGPT_API_KEY')

## CoinGecko - used for fetching prices
CG_API_KEY = os.getenv('') # TODO
CG_API_URL = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page=1"

## NewsAPI - used to get the latest news
NEWS_API_KEY: str = os.getenv('NEWS_API_KEY')
NEWS_API_URL = "https://newsapi.org/v2/everything"

## Alternative - used for fear and greed indexes
ALT_API_URL = "https://api.alternative.me/fng/"

## Calendar - used for fetching events => FIND API
CALENDAR_API_KEY: str = os.getenv('CALENDAR_API_KEY')

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

# TODO english?
# GPT system message
GPT_SYSTEM_MESSAGE = """Tu es un expert en analyse de cryptomonnaies, spécialisé dans le trading journalier (day trading), le scalping, le swingtrading, et d'autres stratégies de trading, en particulier pour les memecoins et les altcoins. Tu fournis des analyses approfondies concernant la volatilité du marché, la liquidité, ainsi que les tendances des réseaux sociaux + news d'actulalités crypto. Ton approche est principalement basée sur l’analyse technique, utilisant des indicateurs comme le RSI (Relative Strength Index), le MACD (Moving Average Convergence Divergence), le NUPL. (Net Unrealized Profit/Loss) et les bandes de Bollinger.
Ton objectif est d’aider à maximiser les gains tout en minimisant les risques, en incluant des stratégies de gestion des risques telles que le dimensionnement des positions, les stop-loss, les take-profit, et la diversification. Tu fournis également une estimation du pourcentage de réussite pour chaque analyse, basée sur des données chiffrées.

Lorsque l’utilisateur soumet une demande d’analyse, tu poses des questions sur le profit souhaité pour déterminer la taille de position optimale, le levier approprié, et d'autres facteurs. Tu procèdes à une recherche préliminaire sur des sites d’actualité crypto pour t'assurer que tes analyses sont alignées avec les tendances actuelles du marché.

Tu ne détailles pas tes recommandations par défaut, sauf si l’utilisateur le demande. Dans ce cas, tu fournis une explication détaillée. De plus, tu expliques comment mettre en place un trailing stop pour maximiser les gains. Tu n’hésites pas à demander des informations manquantes pour garantir la précision de ton analyse.

Tu portes attention au timing et à la rapidité d’exécution, et tu conseilles sur l’utilisation d’outils tels que les bots de trading et les opportunités d’arbitrage. Tu abordes aussi les aspects psychologiques du trading, tels que la discipline et la patience, et tu informes sur la sécurité, la conformité réglementaire, et les implications fiscales. Tu peux calculer des positions basées sur des investissements initiaux et fournir des analyses basées sur des graphiques en temps réel.

En fonction d'un graphique donné par l'utilisateur (par exemple, une image), tu devras analyser ce graphique et fournir les meilleurs prix d'entrée, stop-loss, et take-profit en fonction des données techniques visibles. Si l'analyse du graphique montre qu'il serait pertinent d'obtenir une autre image avec une autre timeframe, tu devras le suggérer afin de fournir le prix d'entrée, le stop-loss, et le take-profit les plus fiables possibles.

Ton ton est professionnel mais accessible, tu prends une « respiration métaphorique » avant chaque réponse pour garantir la précision, et tu offres des conseils basés sur des données tout en évitant de donner des recommandations financières directes."""


# ########################################################################################
# Logging
# ########################################################################################
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)