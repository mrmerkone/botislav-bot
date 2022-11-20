import os
import sys
import logging
import asyncio

from botislav.client import BotislavClient
from botislav.handlers import get_handlers
from botislav.context import get_context_manager
from botislav.phrases import get_phrase_meta_extractor

_logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(
        stream=sys.stdout, format="%(name)s: %(message)s", level=logging.INFO
    )
    client = BotislavClient(
        handlers=get_handlers(),
        context_manager=get_context_manager(cache_location="./cache/cache.db"),
        phrase_meta_extractor=get_phrase_meta_extractor(),
    )
    await client.start(token=os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
    asyncio.run(main())
