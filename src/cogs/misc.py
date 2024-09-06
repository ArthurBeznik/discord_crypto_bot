# misc.py

import discord
from discord.ext import commands
from utils.errors import show_help
import logging

logger = logging.getLogger(__name__)

o_embed = discord.Embed(color=discord.Color.orange())  # misc
s_embed = discord.Embed(color=discord.Color.green())  # Success

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Greetings from the bot")
    async def hello(self, ctx):
        """
        !hello
        """
        await ctx.send(f"Yeyow {ctx.author.mention}! Comment i' va?")


    @commands.command(aliases=["c"], description="Mmmh, hot coffee")
    async def coffee(self, ctx):
        """
        !coffee // !c
        """
        o_embed.clear_fields()
        o_embed.set_image(url="https://c.tenor.com/QrDVGQ9cnsMAAAAC/coffee-creamer.gif")
        await ctx.send(f"{ctx.author.mention}", embed=o_embed)


    @commands.command(description="Test")
    async def pcog(self, ctx, cog_name: str = None):
        """
        !pcog <cog_name>
        """
        logger.debug(f"Called pcog, cog_name: {cog_name}")

        if cog_name is None:
            return await show_help(ctx)
        
        cog = self.bot.get_cog(cog_name)
        if cog:
            commands = cog.get_commands()
            command_names = [c.name for c in commands]
            await ctx.send(f"Commands in cog `{cog_name}`: {', '.join(command_names)}")
            logger.info("Sent print cog")
        else:
            await ctx.send(f"No cog found with the name `{cog_name}`.")

async def setup(bot):
    await bot.add_cog(Misc(bot))