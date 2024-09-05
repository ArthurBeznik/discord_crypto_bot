# sentiment_bot.py

import discord
from discord.ext import commands
import praw
from textblob import TextBlob
import os

# Set up Reddit API credentials
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_SECRET = os.getenv('REDDIT_SECRET')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT')

# Initialize Reddit client
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_SECRET,
    user_agent=REDDIT_USER_AGENT
)

class SentimentBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Analyze market sentiment for a cryptocurrency.")
    async def sentiment(self, ctx, crypto: str):
        """
        !sentiment <crypto>
        """
        # Fetch Reddit comments
        subreddit = reddit.subreddit('all')
        comments = subreddit.search(f'{crypto}', limit=100)
        
        sentiment_scores = []
        for comment in comments:
            analysis = TextBlob(comment.body)
            sentiment_scores.append(analysis.sentiment.polarity)
        
        if sentiment_scores:
            average_sentiment = sum(sentiment_scores) / len(sentiment_scores)
            sentiment_message = (
                f"**Sentiment Analysis for {crypto.capitalize()}:**\n"
                f"**Average Sentiment Score:** {average_sentiment:.2f}\n"
                f"A score > 0 indicates positive sentiment, while a score < 0 indicates negative sentiment."
            )
        else:
            sentiment_message = f"No recent sentiment data found for {crypto.capitalize()}."

        await ctx.send(sentiment_message)

    @commands.command(description="Display general crypto market sentiment.")
    async def sentiment_global(self, ctx):
        """
        !sentiment_global
        """
        # Fetch Reddit comments for a general market sentiment
        subreddit = reddit.subreddit('all')
        comments = subreddit.search('crypto', limit=100)
        
        sentiment_scores = []
        for comment in comments:
            analysis = TextBlob(comment.body)
            sentiment_scores.append(analysis.sentiment.polarity)
        
        if sentiment_scores:
            average_sentiment = sum(sentiment_scores) / len(sentiment_scores)
            sentiment_message = (
                f"**Global Cryptocurrency Sentiment:**\n"
                f"**Average Sentiment Score:** {average_sentiment:.2f}\n"
                f"A score > 0 indicates positive sentiment, while a score < 0 indicates negative sentiment."
            )
        else:
            sentiment_message = "No recent global sentiment data found for cryptocurrencies."

        await ctx.send(sentiment_message)

# To add this cog to your bot
async def setup(bot):
    await bot.add_cog(SentimentBot(bot))
