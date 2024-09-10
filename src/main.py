# main.py

import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import logging

from database import DatabaseManager
from utils.errors import handle_check_failure

logging.basicConfig(
    level=logging.INFO,
    # level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s', datefmt='%H:%M:%S', # without date
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

load_dotenv()
GUILD_ID = os.getenv('DISCORD_GUILD_ID')
BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
MY_GUILD = discord.Object(id=GUILD_ID)

# intents = discord.Intents.default()
intents=discord.Intents(
        guilds=True, members=True, messages=True, reactions=True,
        presences=True, message_content=True,
    )

bot = commands.Bot(command_prefix="/", intents=intents)

async def inspect_cog(cog_name: str):
    cog = bot.get_cog(cog_name)
    commands = cog.get_app_commands()
    logger.info([c.name for c in commands])

async def load_cogs():
    """
    Dynamically loads all cogs from the `cogs` folder.
    """
    for filename in os.listdir("src/cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                logger.info(f"Loaded extension: {filename}")
            except Exception as e:
                logger.error(f"Failed to load extension {filename}: {e}")

async def unload_cogs():
    """
    Dynamically loads all cogs from the `cogs` folder.
    """
    for filename in os.listdir("src/cogs"):
        if filename.endswith(".py"):
            try:
                await bot.unload_extension(f"cogs.{filename[:-3]}")
                logger.info(f"Unloaded extension: {filename}")
            except Exception as e:
                logger.error(f"Failed to unload extension {filename}: {e}")

async def remove_cogs():
    for filename in os.listdir("src/cogs"):
        if filename.endswith(".py"):
            try:
                await bot.remove_cog(f"cogs.{filename[:-3]}")
                logger.info(f"Removed extension: {filename}")
            except Exception as e:
                logger.error(f"Failed to remove extension {filename}: {e}")

async def clear_commands():
    bot.tree.clear_commands(guild=MY_GUILD)
    bot.recursively_remove_all_commands()
    await bot.tree.sync(guild=MY_GUILD)

async def sync_tree():
    bot.tree.copy_global_to(guild=MY_GUILD)
    await bot.tree.sync(guild=MY_GUILD)

@bot.event
async def on_ready():
    # # Load cogs and sync tree
    # await load_cogs()
    # bot.tree.copy_global_to(guild=MY_GUILD)
    # await bot.tree.sync(guild=MY_GUILD)
    # logger.info(bot.tree.get_commands(guild=MY_GUILD))

    # # Clear commands, remove cogs, unload cogs and sync tree
    # await clear_commands()
    # await remove_cogs()
    # await unload_cogs()
    # bot.tree.copy_global_to(guild=MY_GUILD)
    # await bot.tree.sync(guild=MY_GUILD)
    # logger.info(bot.tree.get_commands(guild=MY_GUILD))

    # Reload cogs and sync tree
    await load_cogs()
    await sync_tree()
    # logger.info(bot.tree.get_commands(guild=MY_GUILD))

    # Inspect cog
    # await inspect_cog('Misc')

    # Init DB
    bot.db = DatabaseManager()
    await bot.db.initialize()

    # Bot is ready
    logger.info(f"Logged in as {bot.user}")

@bot.event
async def on_command_error(interaction: discord.Interaction, error: Exception):
    logger.error(f"An error occurred: {error}", exc_info=True)
    await handle_check_failure(interaction, error)

bot.run(BOT_TOKEN)
