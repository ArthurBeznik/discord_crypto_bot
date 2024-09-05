# regulatory_news.py

# TODO ????

from discord.ext import commands
import requests
import os

from dotenv import load_dotenv

load_dotenv()
NEWS_KEY = os.getenv('NEWS_API_KEY')
CMC_KEY = os.getenv('CMC_API_KEY')

class RegulatoryNews(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Display the latest news on crypto regulations in a specific country.")
    async def regulation(self, ctx, country: str):
        """
        !regulation <country>
        """
        url = f"https://newsapi.org/v2/everything?q=crypto+regulations+{country}&apiKey={NEWS_KEY}"
        # print(url) # ? debug

        try:
            response = requests.get(url)
            data = response.json()
            # print(data) # ? debug
            
            if 'news' in data:
                news_items = data['news']
                if news_items:
                    news_message = f"**Regulatory News for {country}:**\n"
                    for item in news_items:
                        news_message += f"- {item['title']}: {item['summary']} ({item['date']})\n"
                    await ctx.send(news_message)
                else:
                    await ctx.send(f"No regulatory news found for {country}.")
            else:
                await ctx.send("Error fetching regulatory news. Please try again.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

    # TODO fix data manip
    @commands.command(description="Check whether a specific cryptocurrency complies with regulations in various countries.")
    async def compliance(self, ctx, crypto: str):
        """
        !compliance <crypto>
        """
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': CMC_KEY
        }
        # print(headers) # ? debug

        url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/info?symbol={crypto}"
        # print(url) # ? debug

        try:
            response = requests.get(url, headers=headers)
            data = response.json()
            # print(data) # ? debug

            if 'data' in data and crypto in data['data']:
                crypto_data = data['data'][crypto]
                compliance_info = crypto_data.get('tags', [])  # Using 'tags' as placeholder for compliance info
                compliance_message = f"**Compliance Information for {crypto}:**\n"
                if compliance_info:
                    for tag in compliance_info:
                        compliance_message += f"- {tag}\n"
                else:
                    compliance_message += "No specific compliance information found."
                await ctx.send(compliance_message)
            else:
                await ctx.send(f"No compliance information found for {crypto}.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

# To add this cog to your bot
async def setup(bot):
    await bot.add_cog(RegulatoryNews(bot))

