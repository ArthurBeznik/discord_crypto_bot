# Imports
# ==========================================================================================
import os
import discord
import asyncio
from discord.ext import commands
from dotenv import load_dotenv
import signal
import sys

# Load environment variables
# ==========================================================================================
load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# Embeds for help and error messages
# ==========================================================================================
h_embed = discord.Embed(color=discord.Color.blurple())  # Help
e_embed = discord.Embed(color=discord.Color.red())  # Error

# Bot initialization
# ==========================================================================================
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, case_insensitive=True, help_command=None)
bot.remove_command("help")

# Load cogs
# ==========================================================================================
async def load_extensions():
    """
    Load needed extensions (i.e. Cogs).
    """
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            print(f"Loading extension {filename}")
            await bot.load_extension(f"cogs.{filename[:-3]}")
    print('------')

# Signal handler
# ==========================================================================================
# def signal_handler(sig, frame):
#     print('Caught signal, exiting')
#     asyncio.create_task(bot.close())
#     sys.exit(0)
def signal_handler(sig, frame):
    print('Caught signal, exiting')
    asyncio.run_coroutine_threadsafe(bot.close(), bot.loop)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Main
# ==========================================================================================
async def main():
    """
    Main function to start the bot and handle graceful shutdown.
    """
    try:
        await load_extensions()
        await bot.start(TOKEN)
        await bot.tree.sync()
        for command in bot.commands:
            print(f"Command registered: {command.name}")
    except KeyboardInterrupt:
        print("Bot has been interrupted. Shutting down...")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if not bot.is_closed():
            await bot.close()

# Run the bot
# ==========================================================================================
if __name__ == "__main__":
    asyncio.run(main())
