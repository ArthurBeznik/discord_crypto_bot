# errors.py

import discord
from discord.ext import commands

e_embed = discord.Embed(color=discord.Color.red())  # Error

async def show_help(interaction: discord.Interaction):
    e_embed.clear_fields()
    usage = f"{interaction.command.description}"
    e_embed.add_field(name="Erreur", value=f"Mauvais usage de la commande\n\n**{usage}**")
    await interaction.response.send_message(f"{interaction.user.mention}", embed=e_embed)