# news_trends.py

# TODO trends?

import os
from discord.ext import commands
import requests
from dotenv import load_dotenv
from utils.errors import show_help

load_dotenv()
NEWS_API_KEY = os.getenv('NEWS_API_KEY')

class NewsTrends(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Display the latest news about a specific cryptocurrency.")
    async def news(self, ctx, crypto: str = None):
        """
        !news <crypto>
        """
        if crypto is None:
            return await show_help(ctx)
    
        url = f"https://newsapi.org/v2/everything?q={crypto}&apiKey={NEWS_API_KEY}"
        response = requests.get(url)
        data = response.json()

        if data.get('status') == 'ok' and data.get('articles'):
            articles = data.get('articles')
            news_message = [f"**Latest news for {crypto}:**\n"]
            for article in articles[:5]:  # Display the top 5 articles
                title = article['title']
                url = article['url']
                news_message.append(f"**{title}**\n{url}\n")
            await ctx.send('\n'.join(news_message))
        else:
            await ctx.send("Error fetching news. Please try again.")

    @commands.command(description="Display market trends including most-discussed and most-traded cryptocurrencies.")
    async def trends(self, ctx):
        """
        !trends
        """
        print('Displaying trends') # ? debug

        url = "https://api.coingecko.com/api/v3/search/trending"
        response = requests.get(url)
        data = response.json()
        print(data)

        if 'coins' in data:
            coins = data['coins']
            # print(coins)
            trends_message = "**Current Market Trends:**\n"
            for coin in coins[:5]:  # Display the top 5 trending coins
                name = coin['item']['name']
                symbol = coin['item']['symbol']
                trends_message += f"**{name}** ({symbol})\n"
            await ctx.send(trends_message)
        else:
            await ctx.send("Error fetching trends. Please try again.")

async def setup(bot):
    await bot.add_cog(NewsTrends(bot))
