# errors.py

import discord

from utils.embeds import error_embed
from utils.config import (
    logging,
)

logger = logging.getLogger(__name__)

async def handle_check_failure(interaction: discord.Interaction, error) -> None:
    embed = discord.Embed(color=discord.Color.red())
    embed.title = "Error"

    if isinstance(error, discord.app_commands.errors.CheckFailure):
        embed = error_embed("CheckFailure", str(error))
        logger.error(f"CheckFailure: {error}")
    elif isinstance(error, discord.app_commands.errors.MissingPermissions):
        embed = error_embed("You are missing permissions.", str(error))
        logger.error(f"MissingPermissions: {error}")
    elif isinstance(error, discord.app_commands.errors.CommandInvokeError):
        embed = error_embed("CommandInvokeError", str(error))
        logger.error(f"CommandInvokeError: {error}")
    elif isinstance(error, ValueError):
        embed = error_embed("ValueError", str(error))
        logger.error(f"ValueError: {error}")
    else:
        embed = error_embed("An unexpected error occurred.", str(error))
        logger.error(f"Unexpected error: {error}", exc_info=True)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)
