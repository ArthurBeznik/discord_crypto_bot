# errors.py

import discord
from discord.ext import commands
from discord import app_commands
import logging

e_embed = discord.Embed(color=discord.Color.red())  # Error

logger = logging.getLogger(__name__)

async def show_help(interaction: discord.Interaction):
    e_embed.clear_fields()
    usage = f"{interaction.command.description}"
    e_embed.add_field(name="Erreur", value=f"Mauvais usage de la commande\n\n**{usage}**")
    await interaction.response.send_message(f"{interaction.user.mention}", embed=e_embed)

async def handle_check_failure(interaction: discord.Interaction, error):
    if isinstance(error, discord.app_commands.errors.CheckFailure):
        await interaction.response.send_message("You do not have permission to use this command | CheckFailure", ephemeral=True)
        logger.error(f"{error}")
    elif isinstance(error, discord.app_commands.errors.MissingPermissions):
        await interaction.response.send_message("You do not have permission to use this command. | MissingPermissions", ephemeral=True, embed=e_embed)
        logger.error(f"{error}")
    else:
        await interaction.response.send_message("Error", ephemeral=True)
        logger.error(f"Unexpected error: {error}", exc_info=True)