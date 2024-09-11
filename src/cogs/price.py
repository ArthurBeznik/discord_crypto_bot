# price.py

import discord
from discord.ext import commands
from discord import app_commands
import logging
import requests

from utils.embeds import error_embed, success_embed
from utils.autocomplete import get_crypto_autocomplete_choices

logger = logging.getLogger(__name__)

class Price(commands.GroupCog, name="price"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="single", description="Get the price of a single cryptocurrency")
    @app_commands.rename(crypto="crypto")
    @app_commands.describe(crypto='Name or symbol of the cryptocurrency')
    @app_commands.autocomplete(crypto=get_crypto_autocomplete_choices)
    async def price_single(self, interaction: discord.Interaction, crypto: str):
        """
        /price single <crypto>
        Fetches and returns the price of a single cryptocurrency.
        """
        try:
            logger.info(f'Input crypto: {crypto}')  # Debug log

            # Resolve the cryptocurrency
            # crypto_id = self.crypto_map.get(crypto.lower())
            crypto_id = self.bot.crypto_map.get(crypto.lower())
            logger.info(f"Resolved crypto: {crypto_id}")
            
            if not crypto_id:
                unrecognized_message = f"Unrecognized cryptocurrency: {crypto}"
                logger.warning(unrecognized_message)
                embed = error_embed('Unrecognized cryptocurrency', crypto)
                await interaction.response.send_message(embed=embed)
                return

            # Fetch the price for the single crypto
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies=usd"
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                price_message = f"The current price of {crypto} is ${data.get(crypto_id, {}).get('usd', 'N/A')}"
                logger.info(f"Price fetched successfully for {crypto}: ${data.get(crypto_id, {}).get('usd', 'N/A')}")
                embed = success_embed(price_message, '')
                await interaction.response.send_message(embed=embed)
            else:
                logger.error(f"Error fetching prices for {crypto}. Status code: {response.status_code}")
                await interaction.response.send_message("Error fetching the prices. Please try again.")

        except Exception as e:
            logger.error(f"Exception in price_single: {str(e)}")
            await interaction.response.send_message("An error occurred while fetching the price. Please try again later.")

    @app_commands.command(name="multiple", description="Get the price of multiple cryptocurrencies")
    @app_commands.rename(cryptos="cryptos")
    @app_commands.describe(cryptos='Names or symbols of the cryptocurrencies, separated by spaces')
    async def price_multiple(self, interaction: discord.Interaction, cryptos: str):
        """
        /price multiple <crypto1> <crypto2> ...
        Fetches and returns the price of multiple cryptocurrencies, shows errors for unrecognized ones.
        """
        try:
            logger.info(f'Input cryptos: {cryptos}')  # Debug log
            logger.info(self.bot.crypto_map)

            # Split the input by spaces
            crypto_list_input = cryptos.split()
            resolved_cryptos = []
            unrecognized_cryptos = []

            # Resolve each cryptocurrency
            for crypto in crypto_list_input:
                crypto_id = self.bot.crypto_map.get(crypto.lower())
                if crypto_id:
                    resolved_cryptos.append((crypto, crypto_id))  # Store both the input and resolved id
                else:
                    unrecognized_cryptos.append(crypto)  # Store unrecognized crypto

            # If no valid cryptos were found, return the error
            if not resolved_cryptos and unrecognized_cryptos:
                await interaction.response.send_message(f"Unrecognized cryptocurrencies: {', '.join(unrecognized_cryptos)}")
                logger.warning(f"All provided cryptocurrencies were unrecognized: {', '.join(unrecognized_cryptos)}")
                return

            # Fetch the prices for the resolved cryptos
            crypto_query = ','.join([crypto_id for _, crypto_id in resolved_cryptos])
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_query}&vs_currencies=usd"
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                response_message = []

                # Construct the message for recognized cryptos
                for crypto, crypto_id in resolved_cryptos:
                    price = data.get(crypto_id, {}).get('usd', 'N/A')
                    response_message.append(f"The current price of {crypto} is ${price}")
                    logger.info(f"Price fetched successfully for {crypto}: ${price}")

                # Construct the message for unrecognized cryptos (if any)
                if unrecognized_cryptos:
                    unrecognized_message = f"Unrecognized cryptocurrencies: {', '.join(unrecognized_cryptos)}"
                    response_message.append(unrecognized_message)
                    logger.warning(f"Unrecognized cryptocurrencies: {', '.join(unrecognized_cryptos)}")

                # Send the final message
                await interaction.response.send_message("\n".join(response_message))

            else:
                logger.error(f"Error fetching prices for multiple cryptos. Status code: {response.status_code}")
                await interaction.response.send_message("Error fetching the prices. Please try again.")

        except Exception as e:
            logger.error(f"Exception in price_multiple: {str(e)}")
            await interaction.response.send_message("An error occurred while fetching the prices. Please try again later.")

async def setup(bot):
    await bot.add_cog(Price(bot))
