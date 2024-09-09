import discord

from main import TOKEN, CryptoBot

intents = discord.Intents.default()
intents.message_content = True

bot = CryptoBot(command_prefix='/', intents=intents)
bot.run(TOKEN)