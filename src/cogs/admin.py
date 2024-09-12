import discord
import os
from discord.ext import commands
from discord import app_commands
import logging
from dotenv import load_dotenv

from utils.checks import is_admin

load_dotenv()
MY_GUILD = discord.Object(id=os.getenv('DISCORD_GUILD_ID'))

logger = logging.getLogger(__name__)

class Admin(commands.Cog, name="admin"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @app_commands.command(name='adminonly', description='A command only accessible by admins.')
    @app_commands.default_permissions(administrator=True)
    @is_admin()
    async def admin_only_command(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message('You are an admin and have access to this command!')

    @app_commands.command(name="load", description="Load a new cog")
    @app_commands.rename(cog_name='cog')
    @app_commands.describe(cog_name='Name of the cog to load')
    @app_commands.default_permissions(administrator=True)
    @is_admin()
    async def load(self, interaction: discord.Interaction, cog_name: str) -> None:
        try:
            await self.bot.load_extension(f"cogs.{cog_name}")
            await interaction.response.send_message(f"Loaded extension **{cog_name}.py**")
            logger.info(f"Loaded cog: {cog_name}")
        except Exception as e:
            await interaction.response.send_message(f"Error loading cog: {e}")
            logger.error(f"Failed to load cog: {cog_name}")

    @app_commands.command(name="sync", description="Sync commands to the Discord server")
    @app_commands.default_permissions(administrator=True)
    @is_admin()
    async def sync(self, interaction: discord.Interaction) -> None:
        try:
            await self.bot.tree.sync(guild=MY_GUILD)
            logger.info(self.bot.tree.get_commands(guild=MY_GUILD))
            await interaction.response.send_message(f"Commands synced to guild {MY_GUILD.id}")
            logger.info(f"Synced commands to guild: {MY_GUILD.id}")
        except Exception as e:
            await interaction.response.send_message(f"Error syncing commands: {e}")
            logger.error(f"Failed to sync commands: {e}")

    @app_commands.command(name="remove", description="Remove a specific command from the Discord server")
    @app_commands.rename(command_name='command')
    @app_commands.describe(command_name='Name of the command to remove')
    @app_commands.default_permissions(administrator=True)
    @is_admin()
    async def remove(self, interaction: discord.Interaction, command_name: str) -> None:
        try:
            logger.info(self.bot.tree.get_commands(guild=MY_GUILD))
            self.bot.tree.remove_command(command_name)
            await self.bot.tree.sync(guild=MY_GUILD)
            logger.info(self.bot.tree.get_commands(guild=MY_GUILD))
            await interaction.response.send_message(f"Removed command {command_name} from guild {MY_GUILD.id}")
            logger.info(f"Removed command {command_name} from guild: {MY_GUILD}")
        except Exception as e:
            await interaction.response.send_message(f"Error syncing commands: {e}")
            logger.error(f"Failed to remove command {command_name}: {e}")

    @app_commands.command(name="clear", description="Clear all commands from the server")
    @app_commands.default_permissions(administrator=True)
    @is_admin()
    async def clear(self, interaction: discord.Interaction) -> None:
        try:
            logger.info(self.bot.tree.get_commands(guild=MY_GUILD))
            self.bot.tree.clear_commands(guild=MY_GUILD)
            await self.bot.tree.sync(guild=MY_GUILD)
            logger.info(self.bot.tree.get_commands(guild=MY_GUILD))
            await interaction.response.send_message(f"Cleared all commands from guild {MY_GUILD.id}")
            logger.info(f"Cleared all commands from guild: {MY_GUILD}")
        except Exception as e:
            await interaction.response.send_message(f"Error syncing commands: {e}")
            logger.error(f"Failed to clear commands: {e}")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Admin(bot))
