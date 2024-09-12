# errors.py

import discord
import logging

from utils.embeds import error_embed

logger = logging.getLogger(__name__)

async def handle_check_failure(interaction: discord.Interaction, error) -> None:
    embed = discord.Embed(color=discord.Color.red())
    embed.title = "Error"

    if isinstance(error, discord.app_commands.errors.CheckFailure):
        embed = error_embed("Check Failure", str(error))
        logger.error(f"CheckFailure: {error}")
    elif isinstance(error, discord.app_commands.errors.MissingPermissions):
        embed.description = "**You are missing permissions.**"
        logger.error(f"MissingPermissions: {error}")
    elif isinstance(error, discord.app_commands.errors.CommandInvokeError):
        embed.description = "**CommandInvokeError**"
        logger.error(f"CommandInvokeError: {error}")
    elif isinstance(error, ValueError):
        embed.description = "**ValueError**"
        logger.error(f"ValueError: {error}")
    else:
        embed.description = "**An unexpected error occurred.**"
        logger.error(f"Unexpected error: {error}", exc_info=True)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)
