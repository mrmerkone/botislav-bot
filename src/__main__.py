import os
import logging
import pathlib

from intent import create_intent_matcher
from bot import BotislavBot

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


if __name__ == '__main__':
    intent_paths = list(pathlib.Path("../resources/intents/").glob("*.y*ml"))
    intent_matcher = create_intent_matcher(intent_paths)
    bot = BotislavBot(intent_matcher=intent_matcher)
    bot.run(os.getenv("DISCORD_TOKEN"))
