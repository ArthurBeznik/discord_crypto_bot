# autocomplete.py

# TODO could become discord_helpers.py ?
# TODO find something better for the crypto_map

import discord
from discord import app_commands

from utils.crypto_data import load_crypto_map
from utils.config import (
    logging,
)

logger = logging.getLogger(__name__)

async def crypto_autocomplete(interaction: discord.Interaction, input_value: str)-> (list | list[app_commands.Choice]):
    """_summary_

    Args:
        interaction (discord.Interaction): _description_
        input_value (str): _description_

    Returns:
        _type_: _description_
    """
    logger.info(f"Input: {input_value} | user: {interaction.user.name}") # ? debug

    crypto_map = load_crypto_map()

    # Ignore initial empty input
    if not input_value.strip():
        return []

    # Split the input by spaces, autocomplete only for the last part
    last_input = input_value.split()[-1]
    
    # Search for matches for the last word in the crypto_map
    choices = [app_commands.Choice(name=key, value=key)
               for key in crypto_map if last_input.lower() in key.lower()]
    
    # Return a maximum of 25 autocomplete choices (discord limitations)
    return choices[:25]
