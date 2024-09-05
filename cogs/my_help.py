# help.py

import discord
import os

from discord.ext import commands
# from utils.errors import *
from dotenv import load_dotenv

load_dotenv()
BOT_CHAN = os.getenv('BOT_CHAN')

h_embed = discord.Embed(color=discord.Color.blurple())  # Help
e_embed = discord.Embed(color=discord.Color.red())  # Error

VISIBLE_COGS = [ "Misc", 
                "Price", 
                "Alerts", 
                "TechnicalAnalysis", 
                "HistoricalData", 
                "NewsTrends", 
                "Comparator",
                "MarketData",
                "Portfolio",
                "MarketAlerts"
                ]

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['h'])
    async def help(self, ctx, args=None):
        # display full command list
        command_names_list = [x.name for x in self.bot.commands]
        # cogs_names_list = [x for x in self.bot.cogs]
        if not args:
            h_embed.clear_fields()
            h_embed.set_author(name="Available Commands")
            for cog in self.bot.cogs:
                if cog in VISIBLE_COGS:
                    cog = self.bot.get_cog(cog)
                    cmds = cog.get_commands()
                    cmds_desc = ''
                    for cmd in cmds:
                        cmds_desc += f"{cmd}\t{cmd.help}\n"
                    h_embed.add_field(name=f"{cog.qualified_name}:", value=f"```{cmds_desc}```", inline=False)
            h_embed.set_footer(text="!help <command> or !help <group> to display more")
            return await ctx.send(f"{ctx.author.mention}", embed=h_embed)
        elif args in VISIBLE_COGS:
            cog = self.bot.get_cog(args)
            cmds = cog.get_commands()
            cmds_desc = ''
            for cmd in cmds:
                cmds_desc += f"{cmd}\t{cmd.help}\n"
            h_embed.clear_fields()
            h_embed.set_author(name=f"Group {cog.qualified_name}")
            h_embed.add_field(name=f"{cog.qualified_name}:", value=f"```{cmds_desc}```", inline=False)
            return await ctx.send(f"{ctx.author.mention}", embed=h_embed)
        elif args in command_names_list:
            cmd = self.bot.get_command(args)
            h_embed.clear_fields()
            h_embed.set_author(name=f"Command {cmd}")
            h_embed.add_field(name=f"```{cmd.help}```", value=f"{cmd.description}", inline=False)
            return await ctx.send(f"{ctx.author.mention}", embed=h_embed)
        else:
            e_embed.clear_fields()
            e_embed.add_field(name="Erreur", value="Cette commande n'existe pas")
            return await ctx.send(embed=e_embed)


async def setup(bot):
    await bot.add_cog(Help(bot))