# info.py

import discord
from discord import app_commands
from discord.ext import commands
import logging

from utils.crypto_data import fetch_crypto_info
from utils.autocomplete import crypto_autocomplete
from utils.embeds import error_embed

logger = logging.getLogger(__name__)

class Info(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="info", description="Display comprehensive market information for a cryptocurrency.")
    @app_commands.rename(crypto="crypto")
    @app_commands.describe(crypto="Name or symbol of the cryptocurrency")
    @app_commands.autocomplete(crypto=crypto_autocomplete)
    async def info(self, interaction: discord.Interaction, crypto: str) -> None:
        """
        /info <crypto>: Display comprehensive market information for a cryptocurrency.
        """
        # Resolve the cryptocurrency
        crypto_id = self.bot.crypto_map.get(crypto.lower())
        logger.info(f"Resolved crypto: {crypto_id}")

        # Fetch cryptocurrency data
        data = fetch_crypto_info(crypto_id)

        if data is None:
            embed = error_embed("Error Fetching Data", f"Could not fetch data for {crypto}. Please try again.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Extract relevant information
        market_cap = data.get('market_data', {}).get('market_cap', {}).get('usd', 'N/A')
        volume_24h = data.get('market_data', {}).get('total_volume', {}).get('usd', 'N/A')
        circulating_supply = data.get('market_data', {}).get('circulating_supply', 'N/A')
        total_supply = data.get('market_data', {}).get('total_supply', 'N/A')
        max_supply = data.get('market_data', {}).get('max_supply', 'N/A')
        fully_diluted_market_cap = data.get('market_data', {}).get('fully_diluted_valuation', {}).get('usd', 'N/A')

        # Convert to string if not 'N/A'
        market_cap_str = str(market_cap) if market_cap != 'N/A' else 'N/A'
        volume_24h_str = str(volume_24h) if volume_24h != 'N/A' else 'N/A'

        # Calculate volume/market cap ratio if data is available
        volume_market_cap_ratio = (
            f"{(float(volume_24h_str.replace(',', '').replace('$', '')) / float(market_cap_str.replace(',', '').replace('$', '')) * 100):.2f}%"
            if market_cap_str != 'N/A' and volume_24h_str != 'N/A'
            else 'N/A'
        )

        # Create an embed to display the market information
        embed = discord.Embed(
            title=f"Comprehensive Information for {crypto.upper()}",
            description=f"Here is the comprehensive market data for {crypto.upper()}:\n",
            color=discord.Color.green()
        )
        embed.add_field(name="Market Cap", value=f"${market_cap:,.2f}" if market_cap != 'N/A' else "N/A", inline=False)
        embed.add_field(name="24h Trading Volume", value=f"${volume_24h:,.2f}" if volume_24h != 'N/A' else "N/A", inline=False)
        embed.add_field(name="Volume/Market Cap Ratio (24h)", value=volume_market_cap_ratio, inline=False)
        embed.add_field(name="Circulating Supply", value=f"{circulating_supply:,}" if circulating_supply != 'N/A' else "N/A", inline=False)
        embed.add_field(name="Total Supply", value=f"{total_supply:,}" if total_supply != 'N/A' else "N/A", inline=False)
        embed.add_field(name="Max Supply", value=f"{max_supply:,}" if max_supply != 'N/A' else "N/A", inline=False)
        embed.add_field(name="Fully Diluted Market Cap", value=f"${fully_diluted_market_cap:,.2f}" if fully_diluted_market_cap != 'N/A' else "N/A", inline=False)
        embed.set_footer(text="Data provided by CoinGecko")

        await interaction.response.send_message(embed=embed)
        logger.info(f"Displayed comprehensive market information for {crypto}.")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Info(bot))
