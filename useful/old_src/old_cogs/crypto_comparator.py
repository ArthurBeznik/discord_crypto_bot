# crypto_comparator.py

# TODO indicators ?
# TODO fix data manipulation

from discord.ext import commands
import requests
import pandas as pd
import pandas_ta as ta
from utils.errors import show_help
import logging

logger = logging.getLogger(__name__)

class CryptoComparator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Compare two cryptocurrencies in terms of price, market cap, volume, etc.")
    async def compare(self, ctx, crypto1: str = None, crypto2: str = None):
        """
        !compare <crypto1> <crypto2>
        """
        logger.debug(f"Called compare, crypto1: {crypto1}, crypto2: {crypto2} | author: {ctx.author.id}")

        if crypto1 is None or crypto2 is None:
            return await show_help(ctx)
        
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto1},{crypto2}&vs_currencies=usd&include_market_cap=true&include_24hr_vol=true"
        response = requests.get(url)
        data = response.json()

        # TODO fix data manipulation
        if crypto1 in data and crypto2 in data:
            price1 = data[crypto1]['usd']
            price2 = data[crypto2]['usd']
            market_cap1 = data[crypto1].get('market_cap', 'N/A')
            market_cap2 = data[crypto2].get('market_cap', 'N/A')
            volume1 = data[crypto1].get('24h_vol', 'N/A')
            volume2 = data[crypto2].get('24h_vol', 'N/A')

            comparison_message = (
                f"**{crypto1}** vs **{crypto2}**\n"
                f"**Price:**\n"
                f"{crypto1}: ${price1}\n"
                f"{crypto2}: ${price2}\n\n"
                f"**Market Cap:**\n"
                f"{crypto1}: ${market_cap1}\n"
                f"{crypto2}: ${market_cap2}\n\n"
                f"**24h Volume:**\n"
                f"{crypto1}: ${volume1}\n"
                f"{crypto2}: ${volume2}\n"
            )
            logger.info(f"Comparison result for {crypto1} and {crypto2}: {comparison_message}")
            await ctx.send(comparison_message)
        else:
            error_message = "Error fetching data for one or both cryptocurrencies. Please check the names and try again."
            logger.error(error_message)
            await ctx.send(error_message)

    async def fetch_historical_data(self, crypto: str = None, days: str = None):
        logger.debug(f"Fetching historical data for {crypto} over {days} days")

        url = f"https://api.coingecko.com/api/v3/coins/{crypto}/market_chart?vs_currency=usd&days={days}"
        response = requests.get(url)
        data = response.json()

        if 'prices' in data:
            df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            logger.info(f"Fetched historical data for {crypto}: {df.head()}")
            return df
        else:
            logger.error(f"No historical data found for {crypto}")
            return None

    @commands.command(description="Compare a specific indicator between two cryptocurrencies.")
    async def compare_indicators(self, ctx, crypto1: str = None, crypto2: str = None, indicator: str = None):
        """
        !compare_indicators <crypto1> <crypto2> <indicator>
        """
        logger.debug(f"Called compare_indicators, crypto1: {crypto1}, crypto2: {crypto2}, indicator: {indicator} | author: {ctx.author.id}")

        if crypto1 is None or crypto2 is None or indicator is None:
            return await show_help(ctx)
        
        logger.info(f"Comparing {crypto1} and {crypto2} on {indicator}")

        # Fetch historical data (e.g., 30 days)
        df1 = await self.fetch_historical_data(crypto1, '30')
        df2 = await self.fetch_historical_data(crypto2, '30')

        if df1 is None or df2 is None:
            error_message = "Error fetching historical data. Please check the cryptocurrency names."
            logger.error(error_message)
            return await ctx.send(error_message)

        # Calculate the chosen indicator
        try:
            if indicator.lower() == 'rsi':
                df1['RSI'] = ta.rsi(df1['price'])
                df2['RSI'] = ta.rsi(df2['price'])
                rsi1 = df1['RSI'].iloc[-1]
                rsi2 = df2['RSI'].iloc[-1]
                result = (
                    f"**RSI Comparison:**\n"
                    f"{crypto1}: {rsi1:.2f}\n"
                    f"{crypto2}: {rsi2:.2f}"
                )
            elif indicator.lower() == 'macd':
                df1['MACD'] = ta.macd(df1['price'])['MACD']
                df2['MACD'] = ta.macd(df2['price'])['MACD']
                macd1 = df1['MACD'].iloc[-1]
                macd2 = df2['MACD'].iloc[-1]
                result = (
                    f"**MACD Comparison:**\n"
                    f"{crypto1}: {macd1:.2f}\n"
                    f"{crypto2}: {macd2:.2f}"
                )
            else:
                error_message = "Unsupported indicator. Please use 'RSI' or 'MACD'."
                logger.error(error_message)
                return await ctx.send(error_message)

            logger.info(f"Indicator comparison result: {result}")
            await ctx.send(result)
        except Exception as e:
            logger.error(f"Exception occurred during indicator comparison: {e}")
            await ctx.send("An error occurred while comparing indicators. Please try again.")

async def setup(bot):
    await bot.add_cog(CryptoComparator(bot))
