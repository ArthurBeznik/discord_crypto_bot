# education_support.py

# TODO implement quiz

from discord.ext import commands
from utils.errors import show_help

class EducationSupport(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Path to lexicon.txt
        self.lexicon = self.load_lexicon('data/lexicon.txt')

    def load_lexicon(self, file_path):
        lexicon = {}
        with open(file_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if ':' in line:
                    term, definition = line.split(':', 1)
                    lexicon[term.strip().lower()] = definition.strip()
        return lexicon

    @commands.command(description="Provide definitions for technical terms related to blockchain and cryptocurrencies.")
    async def lexicon(self, ctx, term: str = None):
        """
        !lexicon <term>
        """
        if term is None:
            return await show_help(ctx)

        term = term.lower()
        definition = self.lexicon.get(term)
        
        if definition:
            await ctx.send(f"**{term.capitalize()}:** {definition}")
        else:
            await ctx.send(f"No definition found for '{term}'. Please try another term.")

    @commands.command(description="Offer quizzes to test the community's knowledge of cryptocurrencies.")
    async def quiz(self, ctx, theme: str = None):
        """
        !quiz <theme>
        """
        if theme is None:
            return await show_help(ctx)

        # TODO implement quiz
        quiz_message = f"Quiz on {theme} is not yet implemented."
        await ctx.send(quiz_message)

async def setup(bot):
    await bot.add_cog(EducationSupport(bot))
