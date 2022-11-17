from contextlib import contextmanager
from logging import getLogger
from typing import Optional

import ctor
import discord
import pickledb
from attr import dataclass

from botislav.phrases import PhraseMeta

_logger = getLogger(__name__)

__all__ = ["Cache", "Context", "ContextManager", "get_context_manager"]


@dataclass(slots=True)
class Cache:
    last_phrase: Optional[str] = None
    opendota_account_id: Optional[str] = None


@dataclass(slots=True)
class Context:
    cache: Cache
    client: discord.Client
    message: discord.Message
    phrase_meta: PhraseMeta

    def normalize_emoji(self, emoji: str) -> str:
        if emoji.startswith("<") and emoji.endswith(">"):
            # already normalized
            return emoji

        emoji = emoji.strip(" \n\r\t:")

        found: discord.Emoji = discord.utils.get(self.client.emojis, name=emoji)
        if found:
            return str(found)

        return f":{emoji}:"


@dataclass(slots=True)
class ContextManager:
    _cache: pickledb.PickleDB

    @contextmanager
    def get_context_from(
        self, client: discord.Client, message: discord.Message, phrase_meta: PhraseMeta
    ) -> Context:
        key = str(message.author.id)
        if raw_cache := self._cache.get(key):
            cache = ctor.load(Cache, raw_cache)
        else:
            cache = Cache()
        context = Context(
            cache=cache, message=message, phrase_meta=phrase_meta, client=client
        )
        yield context
        self._cache.set(key, ctor.dump(context.cache))


def get_context_manager(
    location: str = "cache.db", auto_dump: bool = True
) -> ContextManager:
    cache = pickledb.load(location=location, auto_dump=auto_dump)
    return ContextManager(cache=cache)
