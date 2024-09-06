import discord
from discord import app_commands
from dotenv import load_dotenv
import os

load_dotenv()
GUILD_ID = os.getenv('DISCORD_GUILD_ID')
BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

MY_GUILD = discord.Object(id=GUILD_ID)  # replace with your guild id

class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)

client = MyClient()

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')

# Load cogs
async def load_cogs():
    for filename in os.listdir('cogs'):
        if filename.endswith('.py'):
            cog = filename[:-3]
            await client.load_extension(f'cogs.{cog}')

client.loop.create_task(load_cogs())

client.run(BOT_TOKEN)
