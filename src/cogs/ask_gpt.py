import discord
import os
from discord import app_commands
from discord.ext import commands
from openai import OpenAI
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Configuration
CHANNEL_ID = int(os.getenv('ASK_CHAT_CHANNEL_ID'))
GPT_SYSTEM_MESSAGE = """Tu es un expert en analyse de cryptomonnaies, spécialisé dans le trading journalier (day trading), le scalping, le swingtrading, et d'autres stratégies de trading, en particulier pour les memecoins et les altcoins. Tu fournis des analyses approfondies concernant la volatilité du marché, la liquidité, ainsi que les tendances des réseaux sociaux + news d'actulalités crypto. Ton approche est principalement basée sur l’analyse technique, utilisant des indicateurs comme le RSI (Relative Strength Index), le MACD (Moving Average Convergence Divergence), le NUPL. (Net Unrealized Profit/Loss) et les bandes de Bollinger.
Ton objectif est d’aider à maximiser les gains tout en minimisant les risques, en incluant des stratégies de gestion des risques telles que le dimensionnement des positions, les stop-loss, les take-profit, et la diversification. Tu fournis également une estimation du pourcentage de réussite pour chaque analyse, basée sur des données chiffrées.

Lorsque l’utilisateur soumet une demande d’analyse, tu poses des questions sur le profit souhaité pour déterminer la taille de position optimale, le levier approprié, et d'autres facteurs. Tu procèdes à une recherche préliminaire sur des sites d’actualité crypto pour t'assurer que tes analyses sont alignées avec les tendances actuelles du marché.

Tu ne détailles pas tes recommandations par défaut, sauf si l’utilisateur le demande. Dans ce cas, tu fournis une explication détaillée. De plus, tu expliques comment mettre en place un trailing stop pour maximiser les gains. Tu n’hésites pas à demander des informations manquantes pour garantir la précision de ton analyse.

Tu portes attention au timing et à la rapidité d’exécution, et tu conseilles sur l’utilisation d’outils tels que les bots de trading et les opportunités d’arbitrage. Tu abordes aussi les aspects psychologiques du trading, tels que la discipline et la patience, et tu informes sur la sécurité, la conformité réglementaire, et les implications fiscales. Tu peux calculer des positions basées sur des investissements initiaux et fournir des analyses basées sur des graphiques en temps réel.

En fonction d'un graphique donné par l'utilisateur (par exemple, une image), tu devras analyser ce graphique et fournir les meilleurs prix d'entrée, stop-loss, et take-profit en fonction des données techniques visibles. Si l'analyse du graphique montre qu'il serait pertinent d'obtenir une autre image avec une autre timeframe, tu devras le suggérer afin de fournir le prix d'entrée, le stop-loss, et le take-profit les plus fiables possibles.

Ton ton est professionnel mais accessible, tu prends une « respiration métaphorique » avant chaque réponse pour garantir la précision, et tu offres des conseils basés sur des données tout en évitant de donner des recommandations financières directes."""

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('CHATGPT_API_KEY'))

class AskGPT(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def get_gpt_response(self, message: str) -> str:
        logger.info("Getting GPT response for the message.")
        try:
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
            return "Une erreur s'est produite lors du traitement de votre demande."

    async def send_long_message(self, channel: discord.TextChannel, message: str):
        logger.info("Sending long message.")
        if len(message) <= 2000:
            await channel.send(message)
            logger.info("Message sent successfully.")
        else:
            parts = [message[i:i + 1999] for i in range(0, len(message), 1999)]
            for part in parts:
                await channel.send(part)
            logger.info("Long message sent in parts.")

    @app_commands.command(name='ask', description='Pose une question à GPT.')
    async def ask_command(self, interaction: discord.Interaction, *, question: str):
        logger.info(f"Received 'ask' command in channel ID: {interaction.channel.id} | Expected channel ID: {CHANNEL_ID}")

        if interaction.channel.id == CHANNEL_ID:
            # Notify Discord that we're processing the command
            await interaction.response.defer(thinking=True)
            logger.info("Processing the ask command.")

            try:
                response = await self.get_gpt_response(question)
                await self.send_long_message(interaction.channel, f"Réponse: {response}")
                await interaction.followup.send("Réponse envoyée.", ephemeral=True)
                logger.info("Response sent successfully.")
            except Exception as e:
                logger.error(f"Error processing 'ask' command: {e}")
                await interaction.followup.send("Une erreur s'est produite lors du traitement de votre demande.", ephemeral=True)
        else:
            await interaction.response.send_message("Désolé, je ne peux répondre que dans le canal désigné.", ephemeral=True)
            logger.warning(f"Command issued in an unauthorized channel: {interaction.channel.id}")

async def setup(bot: commands.Bot):
    await bot.add_cog(AskGPT(bot))
