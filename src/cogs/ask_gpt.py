# ask_gpt.py

# TODO does it make sense having the client in get_gpt_response ?

import discord
from discord import app_commands
from discord.ext import commands
from openai import OpenAI

from utils.config import (
    ASK_CHAT_CHANNEL_ID,
    CHATGPT_API_KEY,
    GPT_SYSTEM_MESSAGE,
    logging
)

logger = logging.getLogger(__name__)

class AskGPT(commands.Cog, name="askGPT"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def get_gpt_response(self, message: str) -> str:
        logger.info("Getting GPT response for the message.")
        try:
            client = OpenAI(api_key=CHATGPT_API_KEY)

            response = client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=[
                    {"role": "system", "content": GPT_SYSTEM_MESSAGE},
                    {"role": "user", "content": message}
                ],
                max_tokens=1000
            )
            response_text = response.choices[0].message.content
            logger.info("Successfully received GPT response.")
            return response_text
        except Exception as e:
            logger.error(f"Error in get_gpt_response: {e}")
            return "An error occured while processing your request." 

    async def send_long_message(self, channel: discord.TextChannel, message: str) -> None:
        logger.info("Sending long message.")
        if len(message) <= 2000:
            await channel.send(message)
            logger.info("Message sent successfully.")
        else:
            parts = [message[i:i + 1999] for i in range(0, len(message), 1999)]
            for part in parts:
                await channel.send(part)
            logger.info("Long message sent in parts.")

    @app_commands.command(name='ask', description='Ask something to GPT.')
    async def ask(self, interaction: discord.Interaction, *, question: str) -> None:
        logger.info(f"Received 'ask' command in channel ID: {interaction.channel.id} | Expected channel ID: {ASK_CHAT_CHANNEL_ID}")

        if interaction.channel.id == ASK_CHAT_CHANNEL_ID:
            # Notify Discord that we're processing the command
            await interaction.response.defer(thinking=True)
            logger.info("Processing the ask command.")

            try:
                response = await self.get_gpt_response(question)
                await self.send_long_message(interaction.channel, f"Response: {response}")
                await interaction.followup.send("Response sent.", ephemeral=True)
                logger.info("Response sent successfully.")
            except Exception as e:
                logger.error(f"Error processing 'ask' command: {e}")
                await interaction.followup.send("An error occured while processing your request.", ephemeral=True)
        else:
            await interaction.response.send_message("Sorry, I can only reply in the designated channel [ask-gpt]", ephemeral=True)
            logger.warning(f"Command issued in an unauthorized channel: {interaction.channel.id}")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AskGPT(bot))
