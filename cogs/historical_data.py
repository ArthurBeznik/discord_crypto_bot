# historical_data.py

import discord
from discord.ext import commands
import requests
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from utils.errors import show_help

class HistoricalData(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Generate a graph with historical data for a cryptocurrency over a specific period.")
    async def graphic(self, ctx, crypto: str = None, period: str = None):
        """
        !graphic <crypto> <period>
        """
        if crypto is None or period is None:
            return await show_help(ctx)

        # Define the period mapping
        period_mapping = {
            "1d": "1",
            "1w": "7",
            "1m": "30",
            "3m": "90",
            "6m": "180",
            "1y": "365"
        }

        days = period_mapping.get(period.lower())
        if not days:
            await ctx.send("Invalid period. Use 1d, 1w, 1m, 3m, 6m, or 1y.")
            return

        # Fetch historical data
        url = f"https://api.coingecko.com/api/v3/coins/{crypto}/market_chart?vs_currency=usd&days={days}"
        response = requests.get(url)
        data = response.json()

        if "prices" not in data:
            await ctx.send("Error fetching data. Please try again.")
            return

        # Convert data to DataFrame
        df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)

        # Plot the data
        plt.figure(figsize=(10, 6))
        plt.plot(df.index, df['price'], label=f'{crypto} Price')
        plt.xlabel('Date')
        plt.ylabel('Price (USD)')
        plt.title(f'{crypto} Historical Price Data')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()

        # Save plot to BytesIO object
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()

        # Send the plot to Discord
        file = discord.File(buf, filename='graphic.png')
        await ctx.send(file=file)

    @commands.command(description="Provide detailed historical data in tabular form for analysis.")
    async def history(self, ctx, crypto: str = None, period: str = None):
        """
        !history <crypto> <period>
        """
        if crypto is None or period is None:
            return await show_help(ctx)
    
        # Define the period mapping
        period_mapping = {
            "1d": "1",
            "1w": "7",
            "1m": "30",
            "3m": "90",
            "6m": "180",
            "1y": "365"
        }

        days = period_mapping.get(period.lower())
        if not days:
            await ctx.send("Invalid period. Use 1d, 1w, 1m, 3m, 6m, or 1y.")
            return

        # Fetch historical data
        url = f"https://api.coingecko.com/api/v3/coins/{crypto}/market_chart?vs_currency=usd&days={days}"
        response = requests.get(url)
        data = response.json()

        if "prices" not in data:
            await ctx.send("Error fetching data. Please try again.")
            return

        # Convert data to DataFrame
        df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

        # Create a response message
        response_message = (
            f"**Historical Data for {crypto} over the last {period}:**\n\n"
            f"{df.head(10).to_string(index=False)}\n\n"  # Display the first 10 rows for brevity
            f"To see more data, please use the command with a longer period."
        )

        await ctx.send(response_message)

async def setup(bot):
    await bot.add_cog(HistoricalData(bot))
