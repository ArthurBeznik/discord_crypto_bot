# errors.py

import discord

from discord.ext import commands

e_embed = discord.Embed(color=discord.Color.red())  # Error


async def not_mover_error(ctx):
    e_embed.clear_fields()
    e_embed.add_field(name="Erreur", value="Tu n'es pas mover")
    await ctx.send(f"{ctx.author.mention}", embed=e_embed)


async def not_muter_error(ctx):
    e_embed.clear_fields()
    e_embed.add_field(name="Erreur", value="Tu n'es pas muter")
    await ctx.send(f"{ctx.author.mention}", embed=e_embed)


async def member_not_found_error(ctx, member):
    e_embed.clear_fields()
    e_embed.add_field(name="Erreur", value=f"Le membre **{member}** n'existe pas")
    await ctx.send(f"{ctx.author.mention}", embed=e_embed)


async def channel_not_found_error(ctx, channel):
    e_embed.clear_fields()
    e_embed.add_field(name="Erreur", value=f"Le channel **{channel}** n'existe pas")
    await ctx.send(f"{ctx.author.mention}", embed=e_embed)


async def cm_not_found_error(ctx, channel, member):
    e_embed.clear_fields()
    e_embed.add_field(name="Erreur", value=f"**{member}** et **{channel}** n'existent pas")
    await ctx.send(f"{ctx.author.mention}", embed=e_embed)


async def not_voice_connected_error(ctx, member):
    e_embed.clear_fields()
    e_embed.add_field(name="Erreur", value=f"**{member}** n'est pas connecte a un VC")
    await ctx.send(f"{ctx.author.mention}", embed=e_embed)


async def already_in_channel_error(ctx, member, channel):
    e_embed.clear_fields()
    e_embed.add_field(name="Erreur", value=f"**{member}** est deja dans **{channel}**")
    await ctx.send(f"{ctx.author.mention}", embed=e_embed)


async def not_in_channel_error(ctx):
    e_embed.clear_fields()
    e_embed.add_field(name="Erreur", value=f"Tu dois etre connecte a un channel")
    await ctx.send(f"{ctx.author.mention}", embed=e_embed)


async def show_help(ctx):
    e_embed.clear_fields()
    usage = f"{ctx.command.help}"
    e_embed.add_field(name="Erreur", value=f"Mauvais usage de la commande\n\n**{usage}**")
    await ctx.send(f"{ctx.author.mention}", embed=e_embed)