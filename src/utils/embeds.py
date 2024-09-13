# embeds.py

# TODO change format?
# TODO make description or title optional?

import discord

def error_embed(title: str, description: str) -> discord.Embed:
    """
    Create a formatted error embed.

    :param title: The title of the embed.
    :param description: The description of the embed, typically the error message.
    :return: A discord.Embed instance.
    """
    embed = discord.Embed(
        title=title,
        description=f"**{description}**",
        color=discord.Color.red()
    )
    return embed

def success_embed(title: str, description: str = None) -> discord.Embed:
    """
    Create a formatted success embed.

    :param title: The title of the embed.
    :param description: The description of the embed, typically the success message.
    :return: A discord.Embed instance.
    """
    if description is None:
        description = ""

    embed = discord.Embed(
        title=title,
        description=f"{description}",
        color=discord.Color.green()
    )
    return embed

def misc_embed(title: str, description: str, image_url: str = None) -> discord.Embed:
    """
    Create a formatted success embed.

    :param title: The title of the embed.
    :param description: The description of the embed, typically the success message.
    :return: A discord.Embed instance.
    """
    embed = discord.Embed(
        title=title,
        description=f"{description}",
        color=discord.Color.orange()
    )

    # Optionally add an image if image_url is provided
    if image_url:
        embed.set_image(url=image_url)

    return embed
