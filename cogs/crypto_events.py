# crypto_events.py

# TODO find API for airdrops
# TODO find API for ICOs

from discord.ext import commands
from datetime import datetime
import requests

class CryptoEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.events = {}  # In-memory storage for events

    @commands.command(description="Display upcoming events for a specific cryptocurrency.")
    async def calendar(self, ctx, crypto: str):
        """
        !calendar <crypto>
        """
        try:
            if crypto not in self.events:
                await ctx.send(f"No events found for `{crypto}`.")
                return
            
            events_list = self.events[crypto]
            if not events_list:
                await ctx.send(f"No upcoming events for `{crypto}`.")
                return
            
            events_message = f"**Upcoming Events for {crypto}:**\n"
            for event in events_list:
                event_date = datetime.strptime(event['date'], "%Y-%m-%d").strftime("%B %d, %Y")
                events_message += f"- {event_date}: {event['description']}\n"
            
            await ctx.send(events_message)
        
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

    @commands.command(description="Add an event to the calendar.")
    async def add_event(self, ctx, crypto: str, date: str, *, description: str):
        """
        !add_event <crypto> <date> <description>
        """
        try:
            # Validate date format
            try:
                event_date = datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                await ctx.send("Invalid date format. Use YYYY-MM-DD.")
                return
            
            if crypto not in self.events:
                self.events[crypto] = []
            
            self.events[crypto].append({
                'date': date,
                'description': description
            })
            
            await ctx.send(f"Event added for `{crypto}` on {event_date.strftime('%B %d, %Y')}: {description}")
        
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

    # TODO find API for airdrops
    @commands.command(description="Display upcoming airdrops for a specific cryptocurrency.")
    async def airdrop(self, ctx, crypto: str):
        """
        !airdrop <crypto>
        """
        # TODO find API
        url = f"https://api.example.com/airdrops?crypto={crypto}"
        # print(url) # ? debug
        try:
            response = requests.get(url)
        except Exception as e:
            print(e)
            await ctx.send("TODO")

        if response.status_code != 200:
            await ctx.send(f"Received {response}")
        data = response.json()

        if 'airdrops' in data and data['airdrops']:
            airdrop_message = f"**Upcoming Airdrops for {crypto.capitalize()}:**\n"
            for airdrop in data['airdrops']:
                airdrop_message += (
                    f"**Title:** {airdrop['title']}\n"
                    f"**Date:** {airdrop['date']}\n"
                    f"**Details:** {airdrop['details']}\n\n"
                )
        else:
            airdrop_message = f"No upcoming airdrops found for {crypto.capitalize()}."

        await ctx.send(airdrop_message)

    # TODO find API for ICOs
    @commands.command(description="Display upcoming or current ICOs for a specific cryptocurrency.")
    async def ico(self, ctx, crypto: str):
        """
        !ico <crypto>
        """
        # TODO find API
        url = "https://api.coingecko.com/api/v3/coins/bitcoin"
        response = requests.get(url)
        try:
            response = requests.get(url)
        except Exception as e:
            print(e)
            await ctx.send("TODO")
            
        data = response.json()

        ico_message = f"**ICOs for {crypto.capitalize()}:**\n"
        ico_message += (
            f"**Name:** {data['name']}\n"
            f"**Symbol:** {data['symbol']}\n"
            f"**Current Price:** ${data['market_data']['current_price']['usd']}\n\n"
        )
        await ctx.send(ico_message)

async def setup(bot):
    await bot.add_cog(CryptoEvents(bot))
