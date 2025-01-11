# response_helpers.py

import discord
from .logger import logging
from .embeds import error_embed, misc_embed, success_embed

logger = logging.getLogger(__name__)


async def send_to_interaction(
    interaction: discord.Interaction, embed: discord.Embed
) -> None:
    """
    Sends an embed message to a specified Discord interaction, either as a response or as a follow-up if the initial response has already been completed.

    Args:
        interaction (discord.Interaction): The Discord interaction to send the message to.
        embed (discord.Embed): The embed message to be sent, containing the formatted content for the user.
    """
    # raise discord.InteractionResponded #? testing
    if not interaction.response.is_done():
        # await interaction.response.send_message(embed=embed, ephemeral=True)
        await interaction.response.send_message(embed=embed)
    else:
        # await interaction.followup.send(embed=embed, ephemeral=True)
        await interaction.followup.send(embed=embed)


async def send_success_response(
    interaction: discord.Interaction, title: str, message: str
) -> None:
    """
    Sends an ***embed*** **success** message to the interaction.

    Args:
        interaction (discord.Interaction): The interaction to send the message to.
        title (str): _description_
        message (str): _description_

    Raises:
        e: _description_
    """
    try:
        embed = success_embed(title, message)
        await send_to_interaction(interaction, embed)
        logger.info(f"Success message sent: {message}")
    except Exception as e:
        logger.debug(f"exception type: {type(e)}")  # ? debug
        raise e


async def send_error_response(
    interaction: discord.Interaction, title: str, message: str
) -> None:
    """
    Sends an ***embed*** **error** message to the interaction.

    Args:
        interaction (discord.Interaction): The interaction to send the message to.
        title (str): _description_
        message (str): _description_

    Raises:
        e: _description_
    """
    try:
        embed = error_embed(title, message)
        await send_to_interaction(interaction, embed)
        logger.info(f"Error message sent: {message}")
    except Exception as e:
        logger.debug(f"exception type: {type(e)}")  # ? debug
        raise e


async def send_misc_response(
    interaction: discord.Interaction,
    title: str,
    message: str,
    image_url: str = None,
) -> None:
    """
    Sends an ***embed*** **misc** message to the interaction.

    Args:
        interaction (discord.Interaction): The interaction to send the message to.
        title (str): The title of the message to send.
        message (str): The misc message to send.
        image_url (str, optional): The link to an image, gif, etc. Defaults to None.

    Raises:
        e: _description_
    """
    try:
        embed = misc_embed(title, message, image_url)
        await send_to_interaction(interaction, embed)
        logger.info(f"Misc message sent: {message}")
    except Exception as e:
        logger.debug(f"exception type: {type(e)}")  # ? debug
        raise e
