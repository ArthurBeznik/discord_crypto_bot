
# CryptoBot

A simple crypto bot.

## Installing

## Run Locally

Clone the project

```bash
  git clone https://github.com/ArthurBeznik/discord_crypto_bot/tree/main
```

Go to the project directory

```bash
  cd discord_crypto_bot
```

Activate virtual environment

```bash
  source venv/Scripts/activate
```

Install dependencies

```bash
  pip install -r requirements.txt
```

Start the bot

```bash
  python src/main.py
```

### Environment Variables

To run this project, you will need to add the following environment variables to your ```.env``` file in the root of the project

```
DISCORD_BOT_TOKEN       - Token of your Discord bot
DISCORD_GUILD_ID        - ID of your discord server (aka guild)
DATABASE_URL            - URL to your database
CHATGPT_API_KEY         - API key for OpenAI
ASK_CHAT_CHANNEL_ID     - ID of the channel to send ask commands
NEWS_API_KEY            - API key for https://newsapi.org/
CMC_API_KEY             - API key for https://coinmarketcap.com/
CG_API_KEY              - API key for https://www.coingecko.com/
```

## Commands

### Price related
```bash
  /price single <crypto>
  /price multiple <crypto1> <crypto2> ...
```

###


## Authors

[@ArthurBeznik](https://github.com/ArthurBeznik)