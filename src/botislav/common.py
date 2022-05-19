from abc import abstractmethod, ABCMeta

from attr import dataclass
from discord import Message


class BotislavError(Exception):
    pass


@dataclass
class Context:
    message: Message


class Action(metaclass=ABCMeta):
    @abstractmethod
    async def run(self, context: Context):
        ...
