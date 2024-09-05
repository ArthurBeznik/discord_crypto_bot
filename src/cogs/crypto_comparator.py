# comparator.py

# TODO indicators ?
# TODO fix data manipulation

from discord.ext import commands
import requests
import pandas as pd
import pandas_ta as ta
from utils.errors import show_help

class CryptoComparator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # TODO market_cap and 24h volume are NA
    @commands.command(description="Compare two cryptocurrencies in terms of price, market cap, volume, etc.")
    async def compare(self, ctx, crypto1: str = None, crypto2: str = None):
        """
        !compare <crypto1> <crypto2>
        """
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
            await ctx.send(comparison_message)
        else:
            await ctx.send("Error fetching data for one or both cryptocurrencies. Please check the names and try again.")

    async def fetch_historical_data(self, crypto: str = None, days: str = None):
        print(f"Fetching historical data of {crypto} for {days} days") # ? debug

        url = f"https://api.coingecko.com/api/v3/coins/{crypto}/market_chart?vs_currency=usd&days={days}"
        response = requests.get(url)
        data = response.json()
        # print(data) # ? debug

        # TODO fix data manipulation
        if 'prices' in data:
            df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            return df
        else:
            return None

    @commands.command(description="Compare a specific indicator between two cryptocurrencies.")
    async def compare_indicators(self, ctx, crypto1: str = None, crypto2: str = None, indicator: str = None):
        """
        !compare_indicators <crypto1> <crypto2> <indicator>
        """
        if crypto1 is None or crypto2 is None or indicator is None:
            return await show_help(ctx)
        
        print(f"Comparing {crypto1} and {crypto2} on {indicator}") # ? debug
        
        # Fetch historical data (e.g., 30 days)
        df1 = await self.fetch_historical_data(crypto1, '30')
        df2 = await self.fetch_historical_data(crypto2, '30')
        # print(df1, df2) # ? debug

        if df1 is None or df2 is None:
            return await ctx.send("Error fetching historical data. Please check the cryptocurrency names.")
            # return

        # Calculate the chosen indicator
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
            return await ctx.send("Unsupported indicator. Please use 'RSI' or 'MACD'.")
            # return

        await ctx.send(result)

async def setup(bot):
    await bot.add_cog(CryptoComparator(bot))
