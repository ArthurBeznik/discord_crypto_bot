# checks.py

import discord
from discord import app_commands
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Fetch admin IDs from environment variable
ADMIN_IDS = set(int(id) for id in os.getenv('ADMIN_IDS', '').split(',') if id)
logger.info(f"ADMIN_IDS: {ADMIN_IDS}") # ? debug

def is_admin():
    # logger.info("is_admin called") # ? debug
    def predicate(interaction: discord.Interaction):
        if interaction.user.id in ADMIN_IDS:
            return True
        else:
            raise app_commands.errors.CheckFailure("You are not an admin.")
    return app_commands.check(predicate)