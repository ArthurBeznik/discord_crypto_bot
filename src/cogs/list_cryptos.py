# list_cryptos.py

# TODO now we have 1471 results, so pages...

import discord
from discord.ext import commands
import requests
import logging

logger = logging.getLogger(__name__)

class CryptoPaginator(discord.ui.View):
    def __init__(self, cryptos, per_page=10):
        super().__init__(timeout=None)  # No timeout for the buttons
        self.cryptos = cryptos
        self.per_page = per_page
        self.current_page = 0
        self.total_pages = (len(cryptos) + per_page - 1) // per_page

    # Function to create the embed for the current page
    def create_embed(self):
        embed = discord.Embed(title="Available Cryptocurrencies", color=0x00ff00)
        start_index = self.current_page * self.per_page
        end_index = start_index + self.per_page
        for crypto in self.cryptos[start_index:end_index]:
            embed.add_field(name=f"{crypto['name']} ({crypto['symbol'].upper()})", value=f"ID: {crypto['id']}", inline=True)
        embed.set_footer(text=f"Page {self.current_page + 1}/{self.total_pages}")
        return embed

    # Next button interaction
    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            await interaction.response.edit_message(embed=self.create_embed(), view=self)

    # Previous button interaction
    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embed=self.create_embed(), view=self)

class ListCrypto(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="list_crypto")
    async def list_crypto(self, ctx):
        """
        Command to list available cryptocurrencies from the CoinGecko API.
        """
        logger.debug(f"Listing availables cryptos, author: {ctx.author.id}")
        
        url = "https://api.coingecko.com/api/v3/coins/list"
        response = requests.get(url)

        if response.status_code == 200:
            cryptos = response.json()

            if not cryptos:
                await ctx.send("No cryptocurrencies found.")
                return

            # Create an instance of the paginator with the list of cryptos
            view = CryptoPaginator(cryptos)
            
            # Send the initial message with the first page of the cryptos and add the paginator buttons
            await ctx.send(embed=view.create_embed(), view=view)
        else:
            await ctx.send("Error fetching the list of cryptocurrencies. Please try again later.")

async def setup(bot):
    await bot.add_cog(ListCrypto(bot))

