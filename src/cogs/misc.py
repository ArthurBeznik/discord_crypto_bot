import discord
from discord import app_commands
from discord.ext import commands
import logging

logger = logging.getLogger(__name__)

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="greetings", description="Say hello!")
    async def greetings(self, interaction: discord.Interaction):
        """
        Greets the user.
        """
        await interaction.response.send_message(f"Hello there, {interaction.user.mention}!")
        logger.info(f"Sent greetings to {interaction.user.mention}")

    @app_commands.command(name="goodbye", description="Say goodbye!")
    async def goodbye(self, interaction: discord.Interaction):
        """
        Says goodbye.
        """
        await interaction.response.send_message(f"Goodbye, {interaction.user.mention}!")
        logger.info(f"Sent farewells to {interaction.user.mention}")

async def setup(bot):
    await bot.add_cog(Misc(bot))
