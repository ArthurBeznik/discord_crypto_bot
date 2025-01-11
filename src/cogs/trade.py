# trade.py

import discord
from discord.ext import commands
from discord import app_commands

from bot import CryptoBot
from utils.response_helpers import send_error_response, send_success_response
from utils.config import TRADE_CHANNEL_ID
from utils.logger import logging

logger = logging.getLogger(__name__)

user_data = {}


class Trade(commands.Cog, name="trade"):
    def __init__(self, bot: CryptoBot) -> None:
        self.bot = bot

    @app_commands.command(name="trade", description="Start a trade")
    @app_commands.describe(
        position_size="What is the size of your position?",
        leverage="What leverage do you wish to use?",
    )
    async def trade(
        self, interaction: discord.Interaction, position_size: int, leverage: int
    ) -> None:
        logger.info(
            f"Creating trade for user [{interaction.user.id}] with ps [{position_size}] and leverage [{leverage}]"
        )
        try:
            # await interaction.response.defer(thinking=True)

            trade_data = {
                "user_id": interaction.user.id,
                "position_size": position_size,
                "leverage": leverage,
            }

            # user: User = await self.bot.fetch_user(interaction.user.id)
            # embed = success_embed("Your information has been successfully saved", "")
            # await user.send(embed=embed)

            await send_success_response(
                interaction,
                "Trade saved",
                "Your trade information has been successfully saved.",
                True,
            )

            # TODO send to specific channel?
            # await send_success_response(
            #     interaction, "", f"```json\n{str(trade_data)}```"
            # )
            trade_channel = self.bot.get_channel(TRADE_CHANNEL_ID)
            await trade_channel.send(f"```json\n{str(trade_data)}```")

        except Exception as e:
            await send_error_response(interaction, "Error creating trade", f"{e}")
            logger.error(
                f"Error processing trade ps [{position_size}] and leverage [{leverage}]: {e}"
            )


async def setup(bot: CryptoBot) -> None:
    await bot.add_cog(Trade(bot))
