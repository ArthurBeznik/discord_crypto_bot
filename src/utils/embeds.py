# embeds.py

# TODO change format?
# TODO make description or title optional?

import discord


def error_embed(title: str, description: str) -> discord.Embed:
    """
    Creates an error-styled embed with a red color theme.

    Args:
        title (str): The title of the embed message, indicating the type of error.
        description (str): A detailed message or description explaining the error.

    Returns:
        discord.Embed: A Discord embed object styled with a red color to signify an error.
    """
    embed = discord.Embed(
        title=title, description=f"{description}", color=discord.Color.red()
    )
    return embed


def success_embed(title: str, description: str = None) -> discord.Embed:
    """
    Creates a success-styled embed with a green color theme.

    Args:
        title (str): The title of the embed message, indicating successful operation.
        description (str, optional): A message or description providing details of the success. Defaults to an empty string if not provided.

    Returns:
        discord.Embed: A Discord embed object styled with a green color to signify success.
    """
    if description is None:
        description = ""

    embed = discord.Embed(
        title=title, description=f"{description}", color=discord.Color.green()
    )
    return embed


def misc_embed(title: str, description: str, image_url: str = None) -> discord.Embed:
    """
    Creates a miscellaneous-styled embed with an orange color theme, optionally including an image.

    Args:
        title (str): The title of the embed message, providing the main topic.
        description (str): A message or description providing further details.
        image_url (str, optional): URL of an image/gif/etc to be embedded. If not provided, no image is included.

    Returns:
        discord.Embed: A Discord embed object styled with an orange color, with an optional image if provided.
    """
    embed = discord.Embed(
        title=title, description=f"{description}", color=discord.Color.orange()
    )

    # Optionally add an image if image_url is provided
    if image_url:
        embed.set_image(url=image_url)

    return embed
