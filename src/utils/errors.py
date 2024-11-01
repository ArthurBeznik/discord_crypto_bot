# errors.py

import asyncio
import discord
import psycopg2

from utils.embeds import error_embed
from utils.logger import logging

logger = logging.getLogger(__name__)


async def handle_check_failure(interaction: discord.Interaction, error) -> None:
    logger.debug(f"exception type: {type(error)}")  # ? debug
    logger.debug(f"error: {error}")  # ? debug

    # Unwrap CommandInvokeError to access the original exception
    if isinstance(error, discord.app_commands.errors.CommandInvokeError):
        error = error.original
        logger.debug(f"error: {type(error)}")  # ? debug

    # ########################################################################################
    # DISCORD
    # ########################################################################################
    if isinstance(error, discord.app_commands.errors.CheckFailure):
        embed = error_embed("CheckFailure", str(error))
        logger.error(f"CheckFailure: {error}")
    elif isinstance(error, discord.app_commands.errors.MissingPermissions):
        embed = error_embed("You are missing permissions.", str(error))
        logger.error(f"MissingPermissions: {error}")
    elif isinstance(error, discord.app_commands.errors.MissingRole):
        embed = error_embed("MissingRole.", str(error))
        logger.error(f"MissingRole: {error}")
    elif isinstance(error, discord.Forbidden):
        embed = error_embed("Forbidden", "I lack permissions to perform this action.")
        logger.error(f"Forbidden: {error}")
    elif isinstance(error, discord.app_commands.errors.CommandOnCooldown):
        embed = error_embed(
            "Cooldown",
            f"Command is on cooldown. Retry in {error.retry_after:.2f} seconds.",
        )
        logger.warning(f"CommandOnCooldown: {error}")
    elif isinstance(error, discord.NotFound):
        embed = error_embed("Not Found", "The requested resource could not be found.")
        logger.warning(f"NotFound: {error}")
    elif isinstance(error, discord.HTTPException):
        embed = error_embed("HTTP Exception", str(error))
        logger.error(f"HTTP Exception: {error}")
    elif isinstance(error, discord.app_commands.errors.BotMissingPermissions):
        embed = error_embed("BotMissingPermissions", str(error))
        logger.error(f"BotMissingPermissions: {error}")
    elif isinstance(error, discord.app_commands.errors.TransformerError):
        embed = error_embed("TransformerError", str(error))
        logger.error(f"TransformerError: {error}")
    elif isinstance(error, discord.errors.InteractionResponded):
        embed = error_embed("InteractionResponded", str(error))
        logger.error(f"InteractionResponded: {error}")

    # ########################################################################################
    # ASYNCIO
    # ########################################################################################
    elif isinstance(error, asyncio.TimeoutError):
        embed = error_embed("Timeout", "Operation timed out. Please try again.")
        logger.error(f"TimeoutError: {error}")

    # ########################################################################################
    # PSYCOPG2
    # ########################################################################################
    elif isinstance(error, psycopg2.errors.SyntaxError):
        embed = error_embed("psycopg2 SyntaxError", str(error))
        logger.error(f"psycopg2 SyntaxError: {error}")
    elif isinstance(error, psycopg2.errors.DatabaseError):
        embed = error_embed("psycopg2 DatabaseError", str(error))
        logger.error(f"psycopg2 DatabaseError: {error}")

    # ########################################################################################
    # BUILTIN
    # ########################################################################################
    elif isinstance(error, ValueError):
        embed = error_embed("ValueError", str(error))
        logger.error(f"ValueError: {error}")
    elif isinstance(error, TypeError):
        embed = error_embed("TypeError", str(error))
        logger.error(f"TypeError: {error}")
    elif isinstance(error, IndexError):
        embed = error_embed("IndexError", str(error))
        logger.error(f"IndexError: {error}")
    elif isinstance(error, KeyError):
        embed = error_embed("KeyError", str(error))
        logger.error(f"KeyError: {error}")
    elif isinstance(error, TimeoutError):
        embed = error_embed("TimeoutError", str(error))
        logger.error(f"TimeoutError: {error}")
    elif isinstance(error, SyntaxError):
        embed = error_embed("SyntaxError", str(error))
        logger.error(f"SyntaxError: {error}")

    # ########################################################################################
    # ELSE
    # ########################################################################################
    else:
        embed = error_embed("An unexpected error occurred", str(error))
        logger.error(f"Unexpected error: {error}", exc_info=True)

    # # Check if the initial response has been sent
    # if not interaction.response.is_done():
    #     await interaction.response.send_message(embed=embed, ephemeral=True)
    # else:
    #     await interaction.followup.send(embed=embed, ephemeral=True)
