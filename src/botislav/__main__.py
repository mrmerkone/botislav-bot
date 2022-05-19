import os
import logging

from botislav.commands import get_action_manager
from botislav.client import BotislavClient

_logger = logging.getLogger(__name__)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")


def main():
    action_manager = get_action_manager()
    logging.basicConfig(level=logging.INFO)
    client = BotislavClient(action_manager=action_manager)
    client.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()
