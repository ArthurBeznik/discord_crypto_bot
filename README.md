
# CryptoBot

A simple crypto bot doing cryto things.

## Installing

Clone the project

```bash
  git clone https://github.com/ArthurBeznik/discord_crypto_bot/tree/main
```

Go to the project directory

```bash
  cd discord_crypto_bot
```

Activate the virtual environment

```bash
  source venv/Scripts/activate
```

Install required dependencies

```bash
  pip install -r requirements.txt
```

## Environment Variables

To run this project, you will need to add the following environment variables to your ```.env``` file in the root of the project (see .env-template)

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

## Run Locally

Start the bot

```bash
  python src/main.py
```
Enjoy!


## Commands

All the commands listed below are slash commands, and have their input(s) autocompleted upon typing.

### Prices
```bash
  /price single <crypto>
  /price multiple <crypto1> <crypto2> ...y
```

### Alerts
```bash
  /alert create <crypto> <treshold>
  /alert cancel <crypto>
  /alert show
```

### Analysis
```bash
  /analyse technical <crypto>
  /analyse advanced <crypto>
  /analyse full <crypto>
```



## Authors

[@ArthurBeznik](https://github.com/ArthurBeznik)