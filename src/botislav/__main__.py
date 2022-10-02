import os
import sys
import logging

from botislav import healthcheck
from botislav.commands import get_action_manager
from botislav.client import BotislavClient

_logger = logging.getLogger(__name__)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")


def main():
    action_manager = get_action_manager()
    logging.basicConfig(
        stream=sys.stdout,
        format="[%(levelname)s][%(asctime)s] %(name)s : %(message)s",
        level=logging.INFO,
    )
    client = BotislavClient(action_manager=action_manager)
    healthcheck.start(client)
    client.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()
