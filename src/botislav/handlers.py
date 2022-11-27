import asyncio
from functools import partial
from typing import Dict, Callable, Awaitable

from botislav.context import BotContext
from botislav.opendota import OpenDotaApi

__all__ = [
    "Handler",
    "get_handlers",
]

Handler = Callable[[BotContext], Awaitable[None]]


async def pubg_lastmatch(context: BotContext) -> None:
    await context.discord_message.reply("Ты что играешь в БАБАДЖИ ???")


async def dota_lastmatch(context: BotContext, opendota_api: OpenDotaApi) -> None:
    await context.reply("Ты что играешь в ДОТУ ???")

    replied = await context.wait_for_reply(10)

    if replied:
        await context.reply("красава")

    else:
        await context.reply("че молчишь")


async def greeting(context: BotContext) -> None:
    await context.reply("Здарова")


async def silence(_context: BotContext) -> None:
    pass


def get_handlers() -> Dict[str, Handler]:
    return {
        "dota_lastmatch": partial(dota_lastmatch, opendota_api=OpenDotaApi()),
        "pubg_lastmatch": pubg_lastmatch,
        "greeting": greeting,
        "silence": silence,
    }
