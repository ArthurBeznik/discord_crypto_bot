# events.py

import discord
import os
from discord.ext import commands
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()
GUILD_ID = os.getenv('DISCORD_GUILD_ID')

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Triggered when the bot is ready.
        """
        # await self.bot.tree.sync()  # Register slash commands with Discord
        logger.info(f"Logged in as {self.bot.user} (ID: {self.bot.user.id})")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """
        Triggered when a new member joins the server.
        """
        logger.info(f"New member {member} joined the server")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """
        Triggered when a member leaves the server.
        """
        logger.info(f"Member {member} left the server")

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        Triggered when a message is sent in a channel.
        """
        # Avoid responding to the bot's own messages
        if message.author == self.bot.user:
            return
        
        # Check if the word "samulel" is in the message content (case-insensitive)
        if "samulel" in message.content.lower():
            try:
                # Send a private message to the user
                await message.author.send("C'est un gate ca")
                logger.info(f"Sent DM to {message.author} in response to 'samulel'")
            except discord.Forbidden:
                # Handle the case where the bot is not allowed to send DMs
                logger.error(f"Failed to send DM to {message.author}. DM permissions might be restricted.")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """
        Triggered when an error occurs during command execution.
        """
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("This command does not exist. Please use a valid command.")
            logger.warning(f"Command not found: {ctx.message.content}")
        else:
            # For other errors, log them and send a generic error message
            logger.error(f"An error occurred: {error}", exc_info=True)
            await ctx.send("An error occurred while processing your command.")

async def setup(bot):
    await bot.add_cog(Events(bot))
