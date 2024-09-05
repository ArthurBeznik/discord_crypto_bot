# technical_analysis.py

from discord.ext import commands
import requests
import pandas as pd
import ta  # Technical Analysis library

class TechnicalAnalysis(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Provide basic technical analysis including indicators such as RSI, MACD, EMA, etc.")
    async def technical_analysis(self, ctx, crypto: str):
        """
        !technical_analysis <crypto>
        """
        # Fetch historical data from a public API
        url = f"https://api.coingecko.com/api/v3/coins/{crypto}/market_chart?vs_currency=usd&days=30"
        response = requests.get(url)
        data = response.json()

        if "prices" not in data:
            await ctx.send("Error fetching data. Please try again.")
            return

        # Convert data to DataFrame
        df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)

        # Calculate indicators
        df['rsi'] = ta.momentum.RSIIndicator(df['price']).rsi()
        df['macd'] = ta.trend.MACD(df['price']).macd()
        df['ema'] = ta.trend.EMAIndicator(df['price']).ema_indicator()

        # Create response message
        response_message = (
            f"**Technical Analysis for {crypto}**\n"
            f"RSI (14): {df['rsi'].iloc[-1]:.2f}\n"
            f"MACD: {df['macd'].iloc[-1]:.2f}\n"
            f"EMA (14): {df['ema'].iloc[-1]:.2f}"
        )

        await ctx.send(response_message)

    @commands.command(description="Provide advanced analysis including additional indicators, support/resistance, volume, and recommendations.")
    async def advanced_analysis(self, ctx, crypto: str):
        """
        !advanced_analysis <crypto>
        """
        # Fetch historical data from a public API
        url = f"https://api.coingecko.com/api/v3/coins/{crypto}/market_chart?vs_currency=usd&days=30"
        response = requests.get(url)
        data = response.json()

        if "prices" not in data:
            await ctx.send("Error fetching data. Please try again.")
            return

        # Convert data to DataFrame
        df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)

        # Calculate indicators
        df['rsi'] = ta.momentum.RSIIndicator(df['price']).rsi()
        df['macd'] = ta.trend.MACD(df['price']).macd()
        df['ema'] = ta.trend.EMAIndicator(df['price']).ema_indicator()
        df['volume'] = pd.Series(data['total_volumes'], index=df.index)  # Volume data
        
        # Dummy support/resistance and recommendations (implement as needed)
        support = df['price'].min()
        resistance = df['price'].max()
        recommendation = "Buy" if df['rsi'].iloc[-1] < 30 else "Sell" if df['rsi'].iloc[-1] > 70 else "Hold"

        # Create response message
        response_message = (
            f"**Advanced Analysis for {crypto}**\n"
            f"RSI (14): {df['rsi'].iloc[-1]:.2f}\n"
            f"MACD: {df['macd'].iloc[-1]:.2f}\n"
            f"EMA (14): {df['ema'].iloc[-1]:.2f}\n"
            f"Support: ${support:.2f}\n"
            f"Resistance: ${resistance:.2f}\n"
            f"Recommendation: {recommendation}"
        )

        await ctx.send(response_message)

async def setup(bot):
    await bot.add_cog(TechnicalAnalysis(bot))
