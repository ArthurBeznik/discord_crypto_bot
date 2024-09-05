import discord
from discord.ext import commands
from discord import app_commands

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the token from the .env file
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# Define intents and bot prefix
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

# Hello
@bot.tree.command(name='hello')
async def hello(interaction: discord.Interaction):
    print('Sending hello')
    await interaction.response.send_message("Hello there!")

# Start checking for alerts once the bot is ready
@bot.event
async def on_ready():
    # Syncs the commands with Discord's API
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

# Run the bot
bot.run(TOKEN)
