from yaml import safe_load
from typing import Dict, List, Iterable, Optional
from pathlib import Path
from logging import getLogger

from attr import dataclass
from tokema import (
    parse,
    Rule,
    TextQuery,
    ParsingTable,
    ReferenceQuery,
    build_text_parsing_table
)

_logger = getLogger(__name__)

__all__ = [
    "IntentMatcher",
    "create_intent_matcher"
]


def load_intent_files(files: List[Path]) -> Dict[str, List[str]]:
    intents_dict = {}

    for file in files:
        assert file.is_file(), f"{file.name} is not a file"
        with file.open() as f:
            _logger.info(f'Loading intents from {file.name}')
            intents_dict.update(safe_load(f))

    return intents_dict


def iter_rules_from_intents_dict(intents: Dict[str, List[str]]) -> Iterable[Rule]:
    yield Rule('ROOT', queries=(ReferenceQuery('intent'),))
    for intent_name, intent_example_texts in intents.items():
        _logger.info(f"Added intent '{intent_name}'")
        yield Rule('intent', queries=(ReferenceQuery(intent_name),))
        for example_text in intent_example_texts:
            yield Rule(intent_name, queries=(TextQuery(example_text),))


@dataclass(slots=True)
class IntentMatcher:

    table: ParsingTable

    async def match(self, phrase: str) -> Optional[str]:
        tokens = phrase.lower().split()
        results = parse(input_tokens=tokens, table=self.table)

        if not results:
            return None

        intent = results[0].args[0].args[0].rule.production
        _logger.info(f"Matched intent '{intent}'")

        return intent


def create_intent_matcher(intent_examples_paths: List[Path]) -> IntentMatcher:
    intents_dict = load_intent_files(intent_examples_paths)
    rules = list(iter_rules_from_intents_dict(intents_dict))
    intents_parsing_table = build_text_parsing_table(rules)
    return IntentMatcher(table=intents_parsing_table)
