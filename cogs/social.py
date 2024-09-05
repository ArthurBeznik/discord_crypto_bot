# social.py

from discord.ext import commands
import os

from dotenv import load_dotenv

load_dotenv()
SURVEY_CHAN = os.getenv('SURVEY_CHANNEL_ID')

class Social(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.survey_channel_id = SURVEY_CHAN  # Set this to the ID of the channel where surveys will be posted

    @commands.command(description="Share your position or analysis with the community.")
    async def share_position(self, ctx, crypto: str, price: float):
        """
        !share_position <crypto> <price>
        """
        position_message = f"**User {ctx.author.name} has shared their position:**\n" \
                           f"Cryptocurrency: {crypto}\n" \
                           f"Price: ${price:.2f}\n" \
                           f"Feel free to discuss this position here!"
        channel = await self.bot.fetch_channel(self.survey_channel_id) # Use a specific channel or create logic to select one
        if channel:
            try:
                await channel.send(position_message)
                await ctx.send("Your position has been shared with the community!")
            except Exception as e:
                await ctx.send(f"An error occurred while sharing your position: {e}")
        else:
            await ctx.send("Survey channel not found. Please contact the bot administrator.")

    @commands.command(description="Create a community survey on a crypto topic.")
    async def survey(self, ctx, question: str, *options: str):
        """
        !survey "<question>" <option1> <option2>...
        """
        if len(options) < 2:
            await ctx.send("You need to provide at least two options for the survey.")
            return

        survey_message = f"**Survey:** {question}\n"
        for i, option in enumerate(options, start=1):
            survey_message += f"{i}. {option}\n"

        channel = await self.bot.fetch_channel(self.survey_channel_id)
        if channel:
            try:
                message = await channel.send(survey_message)
                for i in range(len(options)):
                    await message.add_reaction(chr(127462 + i)) # Add reactions as voting options
                await ctx.send("Survey created! Please vote by reacting to the message.")
            except Exception as e:
                await ctx.send(f"An error occurred while creating the survey: {e}")
        else:
            await ctx.send("Survey channel not found. Please contact the bot administrator.")

async def setup(bot):
    await bot.add_cog(Social(bot))
