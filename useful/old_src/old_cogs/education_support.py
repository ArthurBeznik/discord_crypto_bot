# education_support.py

# TODO implement quiz

from discord.ext import commands
from utils.errors import show_help
import logging

logger = logging.getLogger(__name__)

class EducationSupport(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Path to lexicon.txt
        self.lexicon = self.load_lexicon('data/lexicon.txt')

    def load_lexicon(self, file_path):
        lexicon = {}
        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()
                for line in lines:
                    if ':' in line:
                        term, definition = line.split(':', 1)
                        lexicon[term.strip().lower()] = definition.strip()
            logger.info(f"Lexicon loaded from {file_path}.")
        except Exception as e:
            logger.error(f"Failed to load lexicon from {file_path}: {e}")
        return lexicon

    @commands.command(description="Provide definitions for technical terms related to blockchain and cryptocurrencies.")
    async def lexicon(self, ctx, term: str = None):
        """
        !lexicon <term>
        """
        logger.debug(f"Called lexicon with term: {term} | author: {ctx.author.id}")

        if term is None:
            return await show_help(ctx)

        term = term.lower()
        definition = self.lexicon.get(term)
        
        if definition:
            await ctx.send(f"**{term.capitalize()}:** {definition}")
            logger.info(f"Definition sent for term: {term}")
        else:
            await ctx.send(f"No definition found for '{term}'. Please try another term.")
            logger.info(f"No definition found for term: {term}")

    @commands.command(description="Offer quizzes to test the community's knowledge of cryptocurrencies.")
    async def quiz(self, ctx, theme: str = None):
        """
        !quiz <theme>
        """
        logger.debug(f"Called quiz with theme: {theme} | author: {ctx.author.id}")

        if theme is None:
            return await show_help(ctx)

        # TODO implement quiz
        quiz_message = f"Quiz on {theme} is not yet implemented."
        await ctx.send(quiz_message)
        logger.info(f"Quiz requested for theme: {theme}. Currently not implemented.")

async def setup(bot):
    await bot.add_cog(EducationSupport(bot))
