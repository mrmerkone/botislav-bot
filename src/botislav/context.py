import asyncio
from typing import Optional
from functools import cached_property

import ctor
import discord
import pickledb
from attr import dataclass

__all__ = ["Cache", "BotContext", "BotContextManager"]


@dataclass(slots=True)
class Cache:
    steam_id: Optional[str] = None
    opendota_id: Optional[str] = None


@dataclass(slots=True)
class BotContext:
    _cache: pickledb.PickleDB
    _message: discord.Message
    _waiter: Optional[asyncio.Event] = None

    @cached_property
    def key(self) -> str:
        return str(self._message.author.id)

    def get_cache(self) -> Cache:
        if raw_cache := self._cache.get(self.key):
            return ctor.load(Cache, raw_cache)
        return Cache()

    def set_cache(self, cache: Cache) -> None:
        self._cache.set(self.key, ctor.dump(cache))

    async def reply_to_user(self, text: str) -> None:
        await self._message.reply(text)

    async def wait_for_user_reply(self, seconds: float = 5) -> bool:
        self._waiter = asyncio.Event()
        try:
            await asyncio.wait_for(self._waiter.wait(), timeout=seconds)
        except asyncio.TimeoutError:
            return False
        return True

    def set_user_reply(self, message: discord.Message) -> None:
        if self._waiter is None:
            raise RuntimeError("Current context is not waiting for reply")
        self._message = message
        self._waiter.set()


@dataclass(slots=True)
class BotContextManager:
    _cache: pickledb.PickleDB

    def get_context_from(self, message: discord.Message) -> BotContext:
        return BotContext(
            message=message,
            cache=self._cache,
        )
