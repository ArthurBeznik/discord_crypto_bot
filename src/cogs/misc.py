# misc.py

import discord
from discord import app_commands
from discord.ext import commands

from utils.embeds import misc_embed, success_embed
from utils.config import (
    logging,
)

logger = logging.getLogger(__name__)

class Misc(commands.Cog, name="misc"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @app_commands.command(name="greetings", description="Say hello!")
    async def greetings(self, interaction: discord.Interaction) -> None:
        """
        Greets the user.
        """
        embed = success_embed(f"Hello there, {interaction.user.name}!", "")
        await interaction.response.send_message(embed=embed)
        logger.info(f"Sent greetings to {interaction.user.name}")

    @app_commands.command(name="goodbye", description="Say goodbye!")
    async def goodbye(self, interaction: discord.Interaction) -> None:
        """
        Says goodbye.
        """
        embed = misc_embed(f"Godspeed, {interaction.user.name}!", "")
        await interaction.response.send_message(embed=embed)
        logger.info(f"Sent farewells to {interaction.user.name}")

    @app_commands.command(name="flemme", description="La flemme")
    async def flemme(self, interaction: discord.Interaction) -> None:
        """
        Flemme
        """
        embed = misc_embed("", "", "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExOWphbGZ5bmxqd3IzdGU5OGo2c3NodTkxYnkycmJmbTRod294anhwbyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/YuexGWhubkGX4I0Q6j/giphy.gif")
        await interaction.response.send_message(embed=embed)
        logger.info(f"Sent flemme to {interaction.user.name}")

    @app_commands.command(name="coffee", description="Mmmh, hot coffee")
    async def coffee(self, interaction: discord.Interaction) -> None:
        """
        Coffee
        """
        embed = misc_embed("", "", "https://c.tenor.com/QrDVGQ9cnsMAAAAC/coffee-creamer.gif")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="mingati", description="C'est un gâté")
    async def mingati(self, interaction: discord.Interaction) -> None:
        """
        C'est un gâté
        """
        embed = misc_embed("", "", "https://media1.tenor.com/m/6DqObjgpaNQAAAAd/sch-cest-un-g%C3%A2t%C3%A9.gif")
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Misc(bot))
