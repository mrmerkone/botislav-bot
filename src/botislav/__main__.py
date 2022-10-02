import os
import sys
import logging
import asyncio

from botislav import healthcheck
from botislav.commands import get_action_manager
from botislav.client import BotislavClient

_logger = logging.getLogger(__name__)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")


async def main():
    action_manager = get_action_manager()
    logging.basicConfig(
        stream=sys.stdout,
        format="[%(levelname)s][%(asctime)s] %(name)s : %(message)s",
        level=logging.INFO,
    )
    client = BotislavClient(action_manager=action_manager)

    await asyncio.gather(
        client.start(DISCORD_TOKEN),
        healthcheck.start(client, 8080)
    )


if __name__ == "__main__":
    asyncio.run(main())
