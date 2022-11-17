from abc import ABCMeta, abstractmethod
from typing import Dict

from botislav.context import Context

__all__ = ["Handler", "GreetingHandler", "LastMatchHandler", "SilenceHandler", "get_handlers"]


class Handler(metaclass=ABCMeta):
    @abstractmethod
    async def handle(self, context: Context) -> None:
        ...


class GreetingHandler(Handler):
    async def handle(self, context: Context) -> None:
        await context.message.reply("Здарова")


class LastMatchHandler(Handler):
    async def handle(self, context: Context) -> None:
        await context.message.reply(
            f"Ты что, играешь в {context.phrase_meta.parameters['game']}"
        )


class SilenceHandler(Handler):
    async def handle(self, context: Context) -> None:
        await context.message.add_reaction(context.normalize_emoji("clueless"))


def get_handlers() -> Dict[str, Handler]:
    return {
        "lastmatch": LastMatchHandler(),
        "greeting": GreetingHandler(),
        "silence": SilenceHandler(),
    }
