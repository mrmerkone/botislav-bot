from abc import abstractmethod, ABCMeta

from discord import Message


class BotislavError(Exception):
    pass


class IAction(metaclass=ABCMeta):
    @abstractmethod
    async def reply(self, message: Message):
        ...
