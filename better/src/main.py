
import logging

import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from cogs import cog_list

logging.basicConfig(
    level=logging.INFO,
    # level=logging.DEBUG,
    # format='%(asctime)s [%(levelname)s] %(name)s: %(message)s', datefmt='%d/%m/%Y %H:%M:%S', # with date
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s', datefmt='%H:%M:%S', # without date
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

class CryptoBot(commands.Bot):
    async def on_ready(self) -> None:
        """
        Message indicating that the bot is online.
        """
        logger.info("Installing cogs...")

        for cog in cog_list:
            await self.add_cog(cog(self))

        logger.info(self.cogs)

        logger.info("Logged in as %s", self.user)

    async def on_message(self, message: discord.message.Message) -> None:  # pylint: disable=W0221
        """Handle message."""
        if message.author == self.user:
            return

        logger.info("Message from %s: %s", message.author, message.content)

        await self.process_commands(message)

if __name__ == '__main__':
    intents = discord.Intents.default()
    intents.message_content = True

    bot = CryptoBot(command_prefix='/', intents=intents)
    bot.run(TOKEN)