import discord
from discord.ext import commands
from discord import app_commands
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class Vote(commands.Cog, name="vote"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="vote", description="Create a poll for community discussions or contests.")
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(question="The poll question.", options="Comma-separated list of options.")
    async def vote(self, interaction: discord.Interaction, question: str, options: str) -> None:
        """
        Command for creating a poll. Only admins can use this command.

        Args:
            interaction (discord.Interaction): The interaction object from the command.
            question (str): The poll question.
            options (str): A comma-separated list of options for the poll.
        """
        # Split the options by commas
        option_list = [opt.strip() for opt in options.split(",")]

        if len(option_list) < 2 or len(option_list) > 10:
            await interaction.response.send_message("You need to provide between 2 and 10 options.", ephemeral=True)
            return

        # Prepare the poll message
        embed = discord.Embed(
            title=f"📊 Poll: {question}",
            description="\n".join([f"{chr(127462 + i)}: {opt}" for i, opt in enumerate(option_list)]),
            color=discord.Color.blue()
        )
        embed.set_footer(text="React with the corresponding letter to vote!")

        # Acknowledge the interaction
        await interaction.response.defer()

        # Send the poll message using followup to get the message object
        poll_message = await interaction.followup.send(embed=embed, wait=True)

        # Add reactions for each option (A, B, C, etc.)
        for i in range(len(option_list)):
            await poll_message.add_reaction(chr(127462 + i)) # Adds reactions A, B, C, ...

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Vote(bot))
