import os
import logging

from botislav.parsing import PhraseParser
from botislav.client import BotislavClient

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


def main():
    client = BotislavClient(parser=PhraseParser())
    client.run(os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
    main()
