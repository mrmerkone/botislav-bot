from logging import getLogger
from typing import Optional, Union

from attr import dataclass
from lark import Lark, UnexpectedInput
from lark.visitors import Transformer, TransformerChain

from botislav.common import Action
from botislav.commands.lastmatch import LastMatchTransformer
from botislav.commands.greeting import GreetingTransformer

_logger = getLogger(__name__)

__all__ = ["ACTIONS_GRAMMAR", "ActionManager", "get_action_manager"]


ACTIONS_GRAMMAR = """
action: lastmatch | greeting

// -- greeting --

greeting: GREETING
GREETING: "прив" "ет"? | "здаров" "а"? | "хай" | "hi" | "hello"

// -- lastmatch --

lastmatch: LASTMATCH ("в"|"in")? game | game LASTMATCH | LASTMATCH

LASTMATCH: ("последняя "? "игра") | ("ласт "? "катка") | "!"? "last" " "? "match" | "!"? "lm"
game: PUBG | DOTA
PUBG: "pubg" | "пубг" | "пабг" | "пабж"
DOTA: ("dota" | "dotes" | "дота" | "доту" | "дока" | "доку") " "? ("2" | "two" | "два")?

%import common.WS_INLINE
%ignore WS_INLINE
"""


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
            _logger.info("No matched action", exc_info=True)


def get_action_manager() -> ActionManager:
    parser = Lark(grammar=ACTIONS_GRAMMAR, start="action")
    transformer = GreetingTransformer() * LastMatchTransformer()
    return ActionManager(parser=parser, transformer=transformer)
