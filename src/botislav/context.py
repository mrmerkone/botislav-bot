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
    discord_client: discord.Client
    discord_message: discord.Message
    phrase_meta: PhraseMeta

    def resolve_emoji(self, emoji: str) -> str:
        emoji = emoji.strip(" \n\r\t:<>")
        if resolved := discord.utils.get(self.discord_client.emojis, name=emoji):
            return str(resolved)
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
            discord_client=client,
            discord_message=message,
            phrase_meta=phrase_meta,
            cache=cache,
        )

        yield context

        cache.last_phrase = message.content
        self._cache.set(key, ctor.dump(context.cache))


def get_context_manager(
    cache_location: str = "cache.db", cache_auto_dump: bool = True
) -> ContextManager:
    cache = pickledb.load(location=cache_location, auto_dump=cache_auto_dump)
    return ContextManager(cache=cache)
