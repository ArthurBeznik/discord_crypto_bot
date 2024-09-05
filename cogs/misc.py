# misc.py

import discord
from discord.ext import commands

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
    async def pcog(self, ctx, cog_name):
        """
        Testing command to list commands in a cog.
        """
        print(f"Printing cog: {cog_name}") # ? debug
        cog = self.bot.get_cog(cog_name)
        if cog:
            commands = cog.get_commands()
            command_names = [c.name for c in commands]
            await ctx.send(f"Commands in cog `{cog_name}`: {', '.join(command_names)}")
        else:
            await ctx.send(f"No cog found with the name `{cog_name}`.")

async def setup(bot):
    await bot.add_cog(Misc(bot))