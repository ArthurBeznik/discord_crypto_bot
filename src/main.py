# main.py

import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import logging

from database.manager import DatabaseManager
from utils.crypto_data import load_crypto_list, load_crypto_map
from utils.errors import handle_check_failure

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
MY_GUILD = discord.Object(id=os.getenv('DISCORD_GUILD_ID'))

# Load environment variables
load_dotenv()

# Define intents
intents = discord.Intents(
    guilds=True, members=True, messages=True, reactions=True,
    presences=True, message_content=True
)

class CryptoBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(command_prefix="/", intents=intents, help_command=None)
        self.db = None
        self.crypto_map = load_crypto_map()
        self.crypto_list = load_crypto_list()

    async def setup_hook(self) -> None:
        """
        This method is called when the bot starts up.
        """
        # Initialize the database
        await self.init_db()

        # Load cogs and sync the tree
        await self.load_cogs()
        await self.sync_tree()

    async def init_db(self) -> None:
        """
        Initialize the database connection and ensure tables are created.
        """
        self.db = DatabaseManager()
        self.db.initialize() # Ensure tables are created

    async def load_cogs(self) -> None:
        """
        Dynamically loads all cogs from the `cogs` folder.
        """
        for filename in os.listdir("src/cogs"):
            if filename.endswith(".py"):
                try:
                    await self.load_extension(f"cogs.{filename[:-3]}")
                    logger.info(f"Loaded extension: {filename}")
                except Exception as e:
                    logger.error(f"Failed to load extension {filename}: {e}")

    async def sync_tree(self) -> None:
        """
        Sync the command tree with the guild.
        """
        guild = discord.Object(id=os.getenv('DISCORD_GUILD_ID'))
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)

    async def on_ready(self) -> None:
        """
        Event called when the bot is ready.
        """
        # Bot is ready
        logger.info(f"Logged in as {self.user}")
        # logger.info(self.tree.get_commands(guild=MY_GUILD))

    async def on_app_command_completion(self, interaction: discord.Interaction, command) -> None:
        """
        Event called when a command is successfully executed.
        """
        full_command_name = interaction.command.name
        split = full_command_name.split(" ")
        executed_command = str(split[0])
        if interaction.guild:
            logger.info(
                f"Executed command: {executed_command} in {interaction.guild.name} (ID: {interaction.guild.id}) by {interaction.user.name} (ID: {interaction.user.id})"
            )
        else:
            logger.info(
                f"Executed command: {executed_command} by {interaction.user.name} (ID: {interaction.user.id}) in DMs"
            )

# Create bot instance and run it
bot = CryptoBot()

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError) -> None:
    logger.error(f"Error on command: {interaction.command.name}")
    await handle_check_failure(interaction, error)

bot.run(os.getenv('DISCORD_BOT_TOKEN'))
