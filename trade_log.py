import discord
from discord.ext import commands
from discord import app_commands
import asyncio

# Configuration du bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Dictionnaire pour stocker les données utilisateur temporaires
user_data = {}


class TradeButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Recevoir les détails", style=discord.ButtonStyle.primary)
    async def trade_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_message(
            "Je vais vous poser quelques questions en MP.", ephemeral=True
        )
        await self.start_trade_dialog(interaction.user)

    async def start_trade_dialog(self, user):
        try:
            # Première question - Taille de position
            await user.send("Quelle est la taille de votre position ?")
            position_size = await bot.wait_for(
                "message",
                timeout=60.0,
                check=lambda m: m.author == user
                and isinstance(m.channel, discord.DMChannel),
            )

            # Deuxième question - Levier
            await user.send("Quel levier souhaitez-vous utiliser ?")
            leverage = await bot.wait_for(
                "message",
                timeout=60.0,
                check=lambda m: m.author == user
                and isinstance(m.channel, discord.DMChannel),
            )

            # Stockage des données
            trade_data = {
                "user_id": user.id,
                "position_size": position_size.content,
                "leverage": leverage.content,
            }

            # Envoi des données dans le channel dédié
            channel = bot.get_channel(
                1326916884880429138
            )  # Remplacer CHANNEL_ID_BOT_DATA par l'ID réel
            await channel.send(f"```json\n{str(trade_data)}```")

            await user.send("Merci ! Vos informations ont été enregistrées.")

        except asyncio.TimeoutError:
            await user.send(
                "Temps écoulé. Veuillez réessayer en cliquant à nouveau sur le bouton."
            )


@bot.event
async def on_ready():
    print(f"Bot connecté en tant que {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Commandes slash synchronisées : {len(synced)}")
    except Exception as e:
        print(e)


@bot.event
async def on_message(message):
    # Vérifier si le message provient du channel de signaux
    if (
        message.channel.id == 1326917091856482438
    ):  # Remplacer CHANNEL_ID_SIGNALS par l'ID réel
        # Channel public pour les notifications
        notification_channel = bot.get_channel(
            CHANNEL_ID_PUBLIC
        )  # Remplacer CHANNEL_ID_PUBLIC par l'ID réel

        # Envoyer la notification avec le bouton
        view = TradeButton()
        await notification_channel.send(
            "Un nouveau trade est disponible. Cliquez sur le bouton pour recevoir les détails.",
            view=view,
        )


@bot.command()
async def test(ctx):
    """Commande de test pour vérifier les fonctionnalités du bot"""
    try: 
        # Test 1 : Vérification de base
        await ctx.send("🔄 Test de base : Bot en ligne !")

        # Test 2 : Simulation d'un signal
        view = TradeButton()
        await ctx.send("📊 Test du bouton de trading", view=view)

        # Test 3 : Vérification des permissions
        notification_channel = bot.get_channel(1326917091856482438)
        if notification_channel:
            await ctx.send("✅ Canal de notification trouvé")
        else:
            await ctx.send("❌ Canal de notification non trouvé")

    except Exception as e:
        await ctx.send(f"❌ Erreur pendant le test : {str(e)}")

