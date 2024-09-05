# events.py

import discord
import discord.ui

from discord.ext import commands

e_embed = discord.Embed(color=discord.Color.red())  # Error
s_embed = discord.Embed(color=discord.Color.green())  # Success
o_embed = discord.Embed(color=discord.Color.orange())  # misc

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Logged in as {self.bot.user} (ID: {self.bot.user.id})')
        print('------')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """
        Bot welcomes newcomers and sends them faction join embed.
        """
        print("member joined")
        # await faction_join(member)
        # await count_members(member)


    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """
        Bot farewells
        """
        print("member remove")
        # await self.bot.get_channel(DEPART_CHAN).send(f"Ciao {member}!")
        # await count_members(member)


    @commands.Cog.listener()
    async def on_message(self, message):
        """
        Bot reacts to message.
        Delete links.
        Censures profanity.
        Only reacts to commands when entered in the bot channel.
        """
        # if message.author.id == BOT_ID:
        #     return
        # await check_badwords(message)
        # if await check_links(message) is True:
        #     return
        # if await check_channel(message) is True:
        #     return
        # await log(message)
        # return await bot.process_commands(message)  # not needed inside a cog

async def setup(bot):
    await bot.add_cog(Events(bot))