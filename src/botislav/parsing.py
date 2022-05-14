from enum import Enum
from typing import Optional
from logging import getLogger

from attr import dataclass
from discord import Message
from lark import Lark, Transformer, UnexpectedInput

from botislav.abc import IAction, BotislavError

_logger = getLogger(__name__)

ACTIONS_GRAMMAR = """
action: last_match
      | hello


// -- ACTIONS --

last_match: LAST_MATCH ("в"|"in")? game
          | game LAST_MATCH

LAST_MATCH: "последняя"? "игра" 
          | "ласт"? "катка"
          | "!"? "last" " "? "match"
          | "!"? "lm"

hello: GREETING

GREETING: "прив" "ет"?
     | "здаров" "а"?
     | "хай"
     | "hi"
     | "hello"


// -- GAME --

game: PUBG | DOTA

PUBG: "pubg"
    | "пубг"

DOTA: "dota"
    | "dotes"
    | "дота"
    | "доту"
    | "дока"
    | "доку"

%import common.WS_INLINE
%ignore WS_INLINE
"""


class Game(Enum):
    PUBG = "PUBG"
    DOTA = "DOTA"


@dataclass
class HelloAction(IAction):
    async def reply(self, message: Message):
        await message.channel.send("здарова")


@dataclass
class DotaLastMatchAction(IAction):
    async def reply(self, message: Message):
        await message.channel.send("dota")


@dataclass
class PubgLastMatchAction(IAction):
    async def reply(self, message: Message):
        await message.channel.send("pubg")


class _AstTransformer(Transformer):

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
    def last_match(self, tokens):
        if game := next(filter(lambda t: isinstance(t, Game), tokens), None):
            if game == Game.DOTA:
                return DotaLastMatchAction()
            if game == Game.PUBG:
                return PubgLastMatchAction()
        raise BotislavError("Unsupported game")

    # noinspection PyMethodMayBeStatic
    def hello(self, _):
        return HelloAction()


@dataclass(slots=True)
class PhraseParser:
    parser: Lark = Lark(ACTIONS_GRAMMAR, start="action")
    transformer: Transformer = _AstTransformer()

    def parse(self, phrase: str) -> Optional[IAction]:
        try:
            tree = self.parser.parse(text=phrase)
            node = self.transformer.transform(tree)
            action = node.children[0]
            _logger.info(f"Matched {action.__class__.__name__}")
            return action
        except UnexpectedInput:
            _logger.debug("No matched action")
