import csv
import random
from pathlib import Path
from typing import Dict, List

from attr import dataclass

__all__ = [
    "PHRASE_GENERATOR"
]

_PHRASES_BY_HERO_CSV_PATH = Path(__file__).parent.joinpath("resources/dota_phrases_by_hero.csv")
_PHRASES_GENERIC_CSV_PATH = Path(__file__).parent.joinpath("resources/dota_phrases_generic.csv")

HeroName = str
Phrase = str
Win = bool


@dataclass(slots=True, frozen=True)
class PhraseGenerator:
    _phrases_by_hero: Dict[HeroName, Dict[Win, Phrase]]
    _phrases_generic: Dict[Win, List[Phrase]]

    def get_phrase(self, win: bool, username: str, hero: str, score: str) -> str:
        choices = []
        if hero in self._phrases_by_hero:
            choices.append(self._phrases_by_hero[hero][win])
        choices.append(random.choice(self._phrases_generic[win]))
        phrase_template = random.choice(choices)
        return phrase_template.format(username=username, hero=hero, score=score)


def get_phrase_generator() -> PhraseGenerator:

    phrases_by_hero: Dict[HeroName, Dict[Win, Phrase]] = {}
    with _PHRASES_BY_HERO_CSV_PATH.open(encoding="utf-8") as file:
        reader = csv.reader(file, delimiter=",")
        for row in list(reader)[1:]:
            if row[0] not in phrases_by_hero:
                phrases_by_hero[row[0]] = {}
            phrases_by_hero[row[0]][True] = row[1]
            phrases_by_hero[row[0]][False] = row[2]

    phrases_generic: Dict[Win, List[Phrase]] = {}
    with _PHRASES_GENERIC_CSV_PATH.open(encoding="utf-8") as file:
        reader = csv.reader(file, delimiter=",")
        phrases_generic[True] = []
        phrases_generic[False] = []
        for row in list(reader)[1:]:
            phrases_generic[True].append(row[0])
            phrases_generic[False].append(row[1])

    return PhraseGenerator(phrases_by_hero=phrases_by_hero, phrases_generic=phrases_generic)


PHRASE_GENERATOR = get_phrase_generator()

