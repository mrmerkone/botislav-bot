from enum import Enum
from typing import Optional

from attr import dataclass
from lark import Transformer

from botislav.common import Action, Context

__all__ = ["Game", "LastMatchAction", "LastMatchTransformer"]


class Game(Enum):
    PUBG = "PUBG"
    DOTA = "DOTA"


@dataclass(slots=True)
class LastMatchAction(Action):
    game: Optional[Game]

    async def run(self, context: Context):
        if self.game == Game.DOTA:
            await context.message.channel.send("dota")
        elif self.game == Game.PUBG:
            await context.message.channel.send("pubg")
        else:
            await context.message.channel.send("no game defined")


class LastMatchTransformer(Transformer):

    # noinspection PyMethodMayBeStatic
    def PUBG(self, _):
        return Game.PUBG

    # noinspection PyMethodMayBeStatic
    def DOTA(self, _):
        return Game.DOTA

    # noinspection PyMethodMayBeStatic
    def game(self, token):
        return token[0]

    # noinspection PyMethodMayBeStatic
    def lastmatch(self, tokens):
        game = next(filter(lambda t: isinstance(t, Game), tokens), None)
        return LastMatchAction(game)
