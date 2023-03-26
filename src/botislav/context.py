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
    _client: discord.Client
    _message: discord.Message
    _reply_queue: asyncio.Queue

    def normalize_emoji(self, emoji: str) -> str:
        if emoji.startswith("<") and emoji.endswith(">"):
            return emoji
        emoji = emoji.strip(" \n\r\t:")
        if found := discord.utils.get(self._client.emojis, name=emoji):
            return str(found)
        return f":{emoji}:"

    @property
    def user_text(self) -> str:
        return self._message.content

    async def reply_to_user(self, text: str) -> None:
        await self._message.reply(text)

    async def reply_to_user_with_embed(self, title: str, description: str, color: int, thumbnail: str) -> None:
        embed = discord.Embed(
            title=title,
            description=description,
            color=color
        )
        embed.set_thumbnail(url=thumbnail)
        await self._message.channel.send(embed=embed, reference=self._message)

    async def send_text(self, text: str) -> None:
        await self._message.channel.send(text)

    async def add_reaction(self, emoji: str) -> None:
        await self._message.add_reaction(emoji)

    async def wait_for_user_reply(self, timeout: float = 5) -> bool:
        reply_wait_task = asyncio.Task(self._reply_queue.get())
        try:
            self._message = await asyncio.wait_for(
                fut=reply_wait_task, timeout=timeout
            )
        except asyncio.TimeoutError:
            reply_wait_task.cancel()
            return False
        return True


@dataclass(slots=True)
class ContextManager:
    _cache: pickledb.PickleDB
    _active_reply_queues: Dict[str, "asyncio.Queue[discord.Message]"] = attrib(factory=dict)

    _client: discord.Client = attrib(init=False)

    def set_client(self, client: discord.Client):
        self._client = client

    @contextmanager
    def get_context(self, key: str, message: discord.Message):
        reply_queue: "asyncio.Queue[discord.Message]" = asyncio.Queue()
        self._active_reply_queues[key] = reply_queue

        if raw_cache := self._cache.get(key):
            cache = ctor.load(Cache, raw_cache)
        else:
            cache = Cache()

        try:

            yield Context(key=key, message=message, cache=cache, reply_queue=reply_queue, client=self._client)

        finally:
            self._active_reply_queues.pop(key)
            self._cache.set(key, ctor.dump(cache))

    def has_active_context(self, key: str) -> bool:
        return key in self._active_reply_queues

    def pass_reply_to_active_context(self, key: str, message: discord.Message) -> None:
        self._active_reply_queues[key].put_nowait(message)
