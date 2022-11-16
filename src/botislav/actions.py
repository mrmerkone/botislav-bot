from logging import getLogger
from typing import Union, Optional, Dict, Any

from attr import dataclass, attrib
from lark.lark import Lark
from lark.lexer import Token
from lark.exceptions import UnexpectedInput
from lark.visitors import Transformer, TransformerChain

from botislav.context import Action

_logger = getLogger(__name__)


__all__ = ["Action", "ActionManager", "ACTIONS_GRAMMAR", "get_action_manager"]


ACTIONS_GRAMMAR = """
action: lastmatch | greeting

// -- greeting --

greeting: GREETING
GREETING: "прив" "ет"? | "здаров" "а"? | "хай" | "hi" | "hello"

// -- lastmatch --

lastmatch: LASTMATCH ("в"|"in")? game | LASTMATCH

LASTMATCH: "лм" | ("последняя "? "игра") | ("ласт "? "катка") | "!"? "last" " "? "match" | "!"? "lm"

game: PUBG | DOTA
PUBG: "pubg" | "пубг" | "пабг" | "пабж" | "бабаджи" | "baba" " "? "gee"
DOTA: ("dota" | "dotes" | "дота" | "доту" | "дока" | "доку") " "? ("2" | "two" | "два")?

%import common.WS_INLINE
%ignore WS_INLINE
"""


@dataclass
class Action:
    id: str
    parameters: Dict[str, Any] = attrib(factory=dict)


@dataclass(slots=True)
class ActionManager:
    parser: Lark
    transformer: Union[Transformer, TransformerChain]

    def get_action(self, phrase: str) -> Optional[Action]:
        try:
            tree = self.parser.parse(phrase)
            node = self.transformer.transform(tree)
            action = node.children[0]
            _logger.info(f"Matched {action.__class__.__name__}")
            return action
        except UnexpectedInput:
            _logger.info("No matched action")
            return None


class LastMatchTransformer(Transformer):

    # noinspection PyMethodMayBeStatic
    def PUBG(self, _):
        return "PUBG"

    # noinspection PyMethodMayBeStatic
    def DOTA(self, _):
        return "DOTA"

    # noinspection PyMethodMayBeStatic
    def game(self, token):
        return token[0]

    # noinspection PyMethodMayBeStatic
    def lastmatch(self, tokens):
        game = next(filter(lambda i: not isinstance(i, Token), tokens), "DOTA")
        return Action(id="lastmatch", parameters={"game": game})


class GreetingTransformer(Transformer):
    # noinspection PyMethodMayBeStatic
    def greeting(self, _):
        return Action(id="greeting")


def get_action_manager() -> ActionManager:
    parser = Lark(grammar=ACTIONS_GRAMMAR, start="action")
    transformer = GreetingTransformer() * LastMatchTransformer()
    return ActionManager(parser=parser, transformer=transformer)
