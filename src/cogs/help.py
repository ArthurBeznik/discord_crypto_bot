# help.py

from typing import Literal
import discord
from discord.ext import commands
from discord import app_commands

from utils.helpers import get_cogs_and_commands
from utils.config import (
    logging,
)

logger = logging.getLogger(__name__)

class Help(commands.Cog, name="help"):
    def __init__(self, bot) -> None:
        self.bot = bot
    
    async def get_command_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice]:
        """_summary_

        Args:
            interaction (discord.Interaction): _description_
            current (str): _description_

        Returns:
            _type_: _description_
        """
        commands = [cmd.name for cmd in self.bot.tree.get_commands() if cmd.name.startswith(current.lower())]
        return [app_commands.Choice(name=cmd, value=cmd) for cmd in commands]

    @app_commands.command(name="help", description="Displays information about commands")
    @app_commands.describe(action="all/command", name="Name of the command")
    @app_commands.autocomplete(name=get_command_autocomplete)
    async def help(self, interaction: discord.Interaction, action: Literal['all', 'command'], name: str = None) -> None:
        """_summary_

        Args:
            interaction (discord.Interaction): _description_
            action (Literal['all', 'command']): _description_
            name (str, optional): _description_. Defaults to None.
        """
        logger.info(f"Action: {action}, Name: {name}") # ? debug

        # Fetch cogs and commands using the helper function
        cogs_and_commands = get_cogs_and_commands(self.bot)
        # logger.info(f"cogs cmds: {cogs_and_commands}") # ? debug

        if action == 'all':
            # Display help for all commands
            embed = discord.Embed(title="Help: All Commands", color=0x00A300)
            embed.add_field(name="For more details on a specific command", value="/help command", inline=False)
            for cog_name, commands_list in cogs_and_commands.items():
                embed.add_field(name=cog_name, value="\n".join(commands_list), inline=False)
            await interaction.response.send_message(embed=embed)
        
        elif action == 'command' and name:
            # Try to find the command (could be a command or a command group)
            command = discord.utils.get(self.bot.tree.get_commands(), name=name.lower())

            if command:
                # Check if the command is a group command
                if isinstance(command, app_commands.Group):
                    # It's a group, so list all subcommands in this group
                    embed = discord.Embed(title=f"Help: Command Group - {command.name}", color=0x00A300)
                    for subcommand in command.commands:
                        embed.add_field(name=f"/{subcommand.qualified_name}", value=subcommand.description or "No description provided", inline=False)
                    await interaction.response.send_message(embed=embed)
                else:
                    # It's a regular command
                    embed = discord.Embed(title=f"Help: Command - {command.name}", color=0x00A300)
                    embed.add_field(name="Description", value=command.description or "No description provided")
                    embed.add_field(name="Usage", value=f"/{command.name}", inline=False)
                    await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(f"No command found with the name `{name}`", ephemeral=True)
        else:
            await interaction.response.send_message("Invalid usage. Please specify a valid command.", ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Help(bot))
