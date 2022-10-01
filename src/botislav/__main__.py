import os
import sys
import logging

from botislav.commands import get_action_manager
from botislav.client import BotislavClient

_logger = logging.getLogger(__name__)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")


def main():
    action_manager = get_action_manager()

    root = logging.getLogger()
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("[%(levelname)s][%(asctime)s] %(name)s : %(message)s")
    handler.setFormatter(formatter)
    root.addHandler(handler)

    client = BotislavClient(action_manager=action_manager)
    client.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()
