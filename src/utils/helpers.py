# helpers.py

import logging

logger = logging.getLogger(__name__)

def get_cogs_and_commands(bot) -> dict:
    """
    Fetches all the cogs and their associated commands (including group commands) from the bot.

    Args:
        bot (commands.Bot): The bot instance.

    Returns:
        dict: A dictionary where keys are cog names and values are lists of commands with details (name, description).
    """
    cogs_and_commands = {}

    # Loop through all cogs in the bot
    for cog_name, cog in bot.cogs.items():
        if cog:
            # Initialize a list to store commands for the cog
            commands_list = []

            # Loop through the commands, including both individual and grouped commands
            for cmd in cog.walk_app_commands():
                command_info = f"/{cmd.qualified_name} - {cmd.description or 'No description provided'}"
                commands_list.append(command_info)

            # Only add cog to the dictionary if it has commands
            if commands_list:
                cogs_and_commands[cog_name] = commands_list

    return cogs_and_commands
