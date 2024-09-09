# crypto_events.py

# TODO find API for airdrops
# TODO find API for ICOs

from discord.ext import commands
from datetime import datetime
import requests
from utils.errors import show_help
import logging

logger = logging.getLogger(__name__)

class CryptoEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.events = {}  # In-memory storage for events

    @commands.command(description="Display upcoming events for a specific cryptocurrency.")
    async def calendar(self, ctx, crypto: str = None):
        """
        !calendar <crypto>
        """
        logger.debug(f"Called calendar with crypto: {crypto} | author: {ctx.author.id}")

        if crypto is None:
            return await show_help(ctx)
        
        try:
            if crypto not in self.events:
                logger.info(f"No events found for {crypto}.")
                await ctx.send(f"No events found for `{crypto}`.")
                return
            
            events_list = self.events[crypto]
            if not events_list:
                logger.info(f"No upcoming events for {crypto}.")
                await ctx.send(f"No upcoming events for `{crypto}`.")
                return
            
            events_message = f"**Upcoming Events for {crypto}:**\n"
            for event in events_list:
                event_date = datetime.strptime(event['date'], "%Y-%m-%d").strftime("%B %d, %Y")
                events_message += f"- {event_date}: {event['description']}\n"
            
            logger.info(f"Events sent for {crypto}: {events_message}")
            await ctx.send(events_message)
        
        except Exception as e:
            logger.error(f"An error occurred while fetching events for {crypto}: {e}")
            await ctx.send(f"An error occurred: {e}")

    @commands.command(description="Add an event to the calendar.")
    async def add_event(self, ctx, crypto: str = None, date: str = None, description: str = None):
        """
        !add_event <crypto> <date> <description>
        """
        logger.debug(f"Called add_event with crypto: {crypto}, date: {date}, description: {description} | author: {ctx.author.id}")

        if crypto is None or date is None or description is None:
            return await show_help(ctx)

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
            
            logger.info(f"Event added for {crypto} on {event_date.strftime('%B %d, %Y')}: {description}")
            await ctx.send(f"Event added for `{crypto}` on {event_date.strftime('%B %d, %Y')}: {description}")
        
        except Exception as e:
            logger.error(f"An error occurred while adding event for {crypto}: {e}")
            await ctx.send(f"An error occurred: {e}")

    # TODO find API for airdrops
    @commands.command(description="Display upcoming airdrops for a specific cryptocurrency.")
    async def airdrop(self, ctx, crypto: str = None):
        """
        !airdrop <crypto>
        """
        logger.debug(f"Called airdrop with crypto: {crypto} | author: {ctx.author.id}")

        if crypto is None:
            return await show_help(ctx)

        # TODO find API
        url = f"https://api.example.com/airdrops?crypto={crypto}"
        logger.debug(f"Fetching airdrops from {url}")

        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"An error occurred while fetching airdrops for {crypto}: {e}")
            await ctx.send("An error occurred while fetching airdrops. Please try again later.")
            return

        data = response.json()

        if 'airdrops' in data and data['airdrops']:
            airdrop_message = f"**Upcoming Airdrops for {crypto.capitalize()}:**\n"
            for airdrop in data['airdrops']:
                airdrop_message += (
                    f"**Title:** {airdrop['title']}\n"
                    f"**Date:** {airdrop['date']}\n"
                    f"**Details:** {airdrop['details']}\n\n"
                )
            logger.info(f"Airdrop details sent for {crypto}: {airdrop_message}")
        else:
            airdrop_message = f"No upcoming airdrops found for {crypto.capitalize()}."
            logger.info(f"No airdrops found for {crypto}")

        await ctx.send(airdrop_message)

    # TODO find API for ICOs
    @commands.command(description="Display upcoming or current ICOs for a specific cryptocurrency.")
    async def ico(self, ctx, crypto: str = None):
        """
        !ico <crypto>
        """
        logger.debug(f"Called ico with crypto: {crypto} | author: {ctx.author.id}")

        if crypto is None:
            return await show_help(ctx)

        # TODO find API
        url = "https://api.coingecko.com/api/v3/coins/bitcoin"  # Placeholder URL
        logger.debug(f"Fetching ICO data from {url}")

        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"An error occurred while fetching ICO data for {crypto}: {e}")
            await ctx.send("An error occurred while fetching ICO data. Please try again later.")
            return
            
        data = response.json()

        ico_message = f"**ICOs for {crypto.capitalize()}:**\n"
        ico_message += (
            f"**Name:** {data['name']}\n"
            f"**Symbol:** {data['symbol']}\n"
            f"**Current Price:** ${data['market_data']['current_price']['usd']}\n\n"
        )
        logger.info(f"ICO details sent for {crypto}: {ico_message}")
        await ctx.send(ico_message)

async def setup(bot):
    await bot.add_cog(CryptoEvents(bot))
