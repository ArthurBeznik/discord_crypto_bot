import discord
from discord import app_commands
from discord.ext import commands
import logging

logger = logging.getLogger(__name__)

o_embed = discord.Embed(color=discord.Color.orange())  # misc
s_embed = discord.Embed(color=discord.Color.green())  # Success

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="greetings", description="Say hello!")
    async def greetings(self, interaction: discord.Interaction):
        """
        Greets the user.
        """
        await interaction.response.send_message(f"Hello there, {interaction.user.mention}!")
        logger.info(f"Sent greetings to {interaction.user.name}")

    @app_commands.command(name="goodbye", description="Say goodbye!")
    async def goodbye(self, interaction: discord.Interaction):
        """
        Says goodbye.
        """
        await interaction.response.send_message(f"Goodbye, {interaction.user.mention}!")
        logger.info(f"Sent farewells to {interaction.user.name}")

    @app_commands.command(name="flemme", description="La flemme")
    async def flemme(self, interaction: discord.Interaction):
        """
        Says flemme.
        """
        o_embed.clear_fields()
        o_embed.set_image(url="https://media1.tenor.com/m/nXNHCwBK_M4AAAAC/lazy-cat.gif")
        await interaction.response.send_message(f"{interaction.user.mention}", embed=o_embed)
        logger.info(f"Sent flemme to {interaction.user.name}")

    @app_commands.command(name="coffee", description="Mmmh, hot coffee")
    async def coffee(self, interaction: discord.Interaction):
        """
        /coffee
        """
        o_embed.clear_fields()
        o_embed.set_image(url="https://c.tenor.com/QrDVGQ9cnsMAAAAC/coffee-creamer.gif")
        await interaction.response.send_message(f"{interaction.user.mention}", embed=o_embed)

async def setup(bot):
    await bot.add_cog(Misc(bot))
