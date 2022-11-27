import os
import sys
import logging
import asyncio

import pickledb

from botislav.dialog import DialogManager
from botislav.client import BotislavClient
from botislav.context import BotContextManager
from botislav.intents import get_intent_classifier
from botislav.handlers import get_handlers


async def main():
    logging.basicConfig(
        stream=sys.stdout, format="%(name)s: %(message)s", level=logging.INFO
    )

    client = BotislavClient(
        dialog_manager=DialogManager(
            intent_classifier=get_intent_classifier(),
            handlers=get_handlers(),
            context_manager=BotContextManager(
                cache=pickledb.load(location="./cache/cache.db", auto_dump=True)
            ),
        )
    )

    await client.start(token=os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
    asyncio.run(main())
