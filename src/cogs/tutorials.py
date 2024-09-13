# tutorials.py

import discord
from discord import app_commands
from discord.ext import commands
import os

from utils.config import (
    logging,
    TUTORIALS_FILE
)

logger = logging.getLogger(__name__)

class Tutorial(commands.Cog, name="tutorial"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    def load_tutorials(self) -> dict:
        """
        Loads the tutorials from a text file and returns them as a dictionary.
        The format in the text file should be:
        [topic]
        Tutorial content...

        Returns:
            dict: A dictionary with topics as keys and tutorial content as values.
        """
        tutorials = {}
        if not os.path.exists(TUTORIALS_FILE):
            logger.error(f"Tutorial file {TUTORIALS_FILE} not found.")
            return tutorials

        try:
            with open(TUTORIALS_FILE, 'r') as file:
                lines = file.readlines()

            topic = None
            content = []

            for line in lines:
                line = line.strip()

                # If the line starts with a topic (e.g., [topic]), treat it as a new tutorial section
                if line.startswith("[") and line.endswith("]"):
                    # If we already have a topic, save the previous one
                    if topic and content:
                        tutorials[topic.lower()] = "\n".join(content)

                    # Start a new topic
                    topic = line[1:-1] # Remove the square brackets
                    content = []
                else:
                    content.append(line)

            # Save the last tutorial in the file
            if topic and content:
                tutorials[topic.lower()] = "\n".join(content)

        except Exception as e:
            logger.error(f"Error reading tutorials file: {e}")

        return tutorials

    async def topic_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        """
        Autocomplete function for the tutorial command.

        Args:
            interaction (discord.Interaction): The interaction object for the command.
            current (str): The current input string for the autocomplete.

        Returns:
            list[app_commands.Choice[str]]: A list of autocomplete choices.
        """
        tutorials = self.load_tutorials()
        topics = [topic for topic in tutorials.keys() if current.lower() in topic]
        return [app_commands.Choice(name=topic.capitalize(), value=topic) for topic in topics]

    @app_commands.command(name="tutorial", description="Generate an interactive tutorial based on a specific topic.")
    @app_commands.describe(topic="The topic for which you want a tutorial (e.g., wallet, technical analysis)")
    @app_commands.autocomplete(topic=topic_autocomplete)
    async def tutorial(self, interaction: discord.Interaction, topic: str) -> None:
        """
        Command to fetch and display a tutorial for the requested topic.

        Args:
            interaction (discord.Interaction): The interaction object for the command.
            topic (str): The topic for the tutorial.
        """
        # Load all available tutorials
        tutorials = self.load_tutorials()

        # Search for the requested topic
        tutorial_content = tutorials.get(topic.lower())

        if tutorial_content:
            # Display the tutorial
            embed = discord.Embed(
                title=f"📘 Tutorial on {topic.capitalize()}",
                description=tutorial_content,
                color=discord.Color.blue()
            )
            await interaction.response.send_message(embed=embed)
        else:
            # If no tutorial was found for the topic
            await interaction.response.send_message(
                f"Sorry, no tutorial found for the topic '{topic}'. Please try another topic.",
                ephemeral=True
            )

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Tutorial(bot))
