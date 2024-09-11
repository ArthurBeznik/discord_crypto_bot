# autocomplete.py

# TODO could become discord_helpers.py ?
# TODO find soomething better for the crypto_map

import discord
import logging

from utils.crypto_data import load_crypto_list

logger = logging.getLogger(__name__)

crypto_map = load_crypto_list()

async def get_crypto_autocomplete_choices(interaction: discord.Interaction, input_value: str):
    """_summary_

    Args:
        interaction (discord.Interaction): _description_
        input_value (str): _description_

    Returns:
        _type_: _description_
    """
    logger.info(f"Input: {input_value} | user: {interaction.user.name}") # ? debug

    # Ignore initial empty input
    if not input_value.strip():
        return []

    # Split the input by spaces, autocomplete only for the last part
    last_input = input_value.split()[-1]
    
    # Search for matches for the last word in the crypto_map
    choices = [discord.app_commands.Choice(name=key, value=key)
               for key in crypto_map if last_input.lower() in key.lower()]
    
    # Return a maximum of 25 autocomplete choices
    return choices[:25]
