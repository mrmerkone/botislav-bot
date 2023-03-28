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
Win = bool
KDA = float


@dataclass(slots=True, frozen=True)
class Phrase:
    kda_range: str
    text: str
    win: bool

    def check(self, win: bool, kda: float) -> bool:
        lower, _, higher = self.kda_range.partition(",")
        return float(lower) <= kda < float(higher) and self.win == win


@dataclass(slots=True, frozen=True)
class PhraseGenerator:
    _phrases_by_hero: Dict[HeroName, Dict[Win, str]]
    _phrases_generic: List[Phrase]

    def get_phrase(self, win: bool, username: str, hero: str, score: str, kda: float) -> str:
        choices = []
        if hero in self._phrases_by_hero:
            choices.append(self._phrases_by_hero[hero][win])
        choices.extend(phrase.text for phrase in self._phrases_generic if phrase.check(win, kda))
        phrase_template = random.choice(choices)
        return phrase_template.format(username=username, hero=hero, score=score)


def get_phrase_generator() -> PhraseGenerator:

    phrases_by_hero: Dict[HeroName, Dict[Win, str]] = {}
    with _PHRASES_BY_HERO_CSV_PATH.open(encoding="utf-8") as file:
        reader = csv.reader(file, delimiter=",")
        for row in list(reader)[1:]:
            if row[0] not in phrases_by_hero:
                phrases_by_hero[row[0]] = {}
            phrases_by_hero[row[0]][True] = row[1]
            phrases_by_hero[row[0]][False] = row[2]

    phrases_generic: List[Phrase] = []
    with _PHRASES_GENERIC_CSV_PATH.open(encoding="utf-8") as file:
        reader = csv.reader(file, delimiter=",")
        for row in list(reader)[1:]:
            phrases_generic.append(Phrase(win=True, text=row[0], kda_range=row[2]))
            phrases_generic.append(Phrase(win=False, text=row[1], kda_range=row[2]))

    return PhraseGenerator(phrases_by_hero=phrases_by_hero, phrases_generic=phrases_generic)

PHRASE_GENERATOR = get_phrase_generator()
