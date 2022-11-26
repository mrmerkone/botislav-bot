from logging import getLogger
from typing import Union, Optional, Any

from attr import dataclass
from lark.lark import Lark
from lark.exceptions import UnexpectedInput
from lark.visitors import Transformer, TransformerChain


_logger = getLogger(__name__)


__all__ = [
    "IntentMeta",
    "IntentClassifier",
    "ACTIONS_GRAMMAR",
    "get_intent_classifier",
]


ACTIONS_GRAMMAR = """
intent: dota_lastmatch | pubg_lastmatch | greeting

// -- greeting --

greeting: GREETING
GREETING: "прив" "ет"? | "здаров" "а"? | "хай" | "hi" | "hello"

// -- lastmatch --

dota_lastmatch: LASTMATCH ("в"|"in")? DOTA | LASTMATCH
pubg_lastmatch: LASTMATCH ("в"|"in")? PUBG

LASTMATCH: "лм" | ("последняя "? "игра") | ("ласт "? "катка") | "!"? "last" " "? "match" | "!"? "lm"

game: PUBG | DOTA
PUBG: "pubg" | "пубг" | "пабг" | "пабж" | "бабаджи" | "baba" " "? "gee"
DOTA: ("dota" | "dotes" | "дота" | "доту" | "дока" | "доку") " "? ("2" | "two" | "два")?

%import common.WS_INLINE
%ignore WS_INLINE
"""


@dataclass
class IntentMeta:
    handler_id: Optional[str] = None


@dataclass(slots=True)
class IntentClassifier:
    parser: Lark
    transformer: Union[Transformer, TransformerChain]

    def get_intent(self, phrase: str) -> IntentMeta:
        try:
            tree = self.parser.parse(phrase)
            node = self.transformer.transform(tree)
            meta = node.children[0]
            _logger.info(f"Matched {meta}")
            return meta
        except UnexpectedInput:
            return IntentMeta(handler_id="silence")


class LastMatchTransformer(Transformer[Any, IntentMeta]):
    # noinspection PyMethodMayBeStatic
    def dota_lastmatch(self, _) -> IntentMeta:
        return IntentMeta(handler_id="dota_lastmatch")

    # noinspection PyMethodMayBeStatic
    def pubg_lastmatch(self, _) -> IntentMeta:
        return IntentMeta(handler_id="pubg_lastmatch")


class GreetingTransformer(Transformer[Any, IntentMeta]):
    # noinspection PyMethodMayBeStatic
    def greeting(self, _) -> IntentMeta:
        return IntentMeta(handler_id="greeting")


def get_intent_classifier() -> IntentClassifier:
    parser = Lark(grammar=ACTIONS_GRAMMAR, start="intent")
    transformer = GreetingTransformer() * LastMatchTransformer()
    return IntentClassifier(parser=parser, transformer=transformer)
