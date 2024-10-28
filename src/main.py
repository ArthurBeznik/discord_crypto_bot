# main.py

from bot import CryptoBot
from utils.errors import handle_check_failure
from utils.config import DISCORD_BOT_TOKEN
from utils.logger import logging

logger = logging.getLogger(__name__)


def main() -> None:
    bot = CryptoBot()
    bot.tree.on_error = handle_check_failure

    try:
        bot.run(DISCORD_BOT_TOKEN)
    except Exception as e:
        logger.error(
            f"An error occurred: {e}",
        )
        exit(420)


if __name__ == "__main__":
    main()
