import asyncio
from typing import Optional, Dict
from contextlib import contextmanager

import ctor
import discord
import pickledb
from attr import dataclass, attrib

__all__ = ["Cache", "Context", "ContextManager"]


@dataclass(slots=True)
class Cache:
    steam_id: Optional[str] = None
    opendota_id: Optional[int] = None


@dataclass(slots=True)
class Context:
    key: str
    cache: Cache
    _message: discord.Message
    _reply_queue: asyncio.Queue

    @property
    def user_text(self) -> str:
        return self._message.content

    async def reply_to_user(self, text: str) -> None:
        await self._message.reply(text)

    async def send_text(self, text: str) -> None:
        await self._message.channel.send(text)

    async def wait_for_user_reply(self, timeout: float = 5) -> bool:
        try:
            self._message = await asyncio.wait_for(
                fut=self._reply_queue.get(), timeout=timeout
            )
        except asyncio.TimeoutError:
            return False
        return True


@dataclass(slots=True)
class ContextManager:
    _cache: pickledb.PickleDB
    _active_reply_queues: Dict[str, asyncio.Queue] = attrib(factory=dict)

    @contextmanager
    def get_context(self, key: str, message: discord.Message) -> Context:
        reply_queue = asyncio.Queue()
        self._active_reply_queues[key] = reply_queue

        if raw_cache := self._cache.get(key):
            cache = ctor.load(Cache, raw_cache)
        else:
            cache = Cache()

        yield Context(key=key, message=message, cache=cache, reply_queue=reply_queue)

        self._active_reply_queues.pop(key)
        self._cache.set(key, ctor.dump(cache))

    def has_active_context(self, key: str) -> bool:
        return key in self._active_reply_queues

    def pass_reply_to_active_context(self, key: str, message: discord.Message) -> None:
        self._active_reply_queues[key].put_nowait(message)
