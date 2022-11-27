import asyncio
from typing import Optional
from logging import getLogger
from functools import cached_property

import ctor
import discord
import pickledb
from attr import dataclass


_logger = getLogger(__name__)

__all__ = ["Cache", "BotContext", "BotContextManager"]


@dataclass(slots=True)
class Cache:
    steam_id: Optional[str] = None
    opendota_id: Optional[str] = None


@dataclass(slots=True)
class BotContext:
    _discord_message: discord.Message
    _cache: pickledb.PickleDB
    _waiter: Optional[asyncio.Event] = None

    @cached_property
    def key(self) -> str:
        return str(self._discord_message.author.id)

    def get_cache(self) -> Cache:
        if raw_cache := self._cache.get(self.key):
            return ctor.load(Cache, raw_cache)
        return Cache()

    def set_cache(self, cache: Cache) -> None:
        self._cache.set(self.key, ctor.dump(cache))

    async def reply(self, text: str) -> None:
        await self._discord_message.reply(text)

    async def wait_for_reply(self, seconds: float = 5) -> bool:
        self._waiter = asyncio.Event()
        try:
            await asyncio.wait_for(self._waiter.wait(), timeout=seconds)
        except asyncio.TimeoutError:
            return False
        return True

    def resume(self, discord_message: discord.Message):
        if self._waiter is None:
            raise RuntimeError("Can not resume current context")
        self._discord_message = discord_message
        self._waiter.set()


@dataclass(slots=True)
class BotContextManager:
    _cache: pickledb.PickleDB

    def get_context_from(self, message: discord.Message) -> BotContext:
        return BotContext(
            discord_message=message,
            cache=self._cache,
        )
