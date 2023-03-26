import json
from datetime import datetime
from time import time
from typing import (
    Union,
    Literal,
    Dict,
    List,
    Optional,
    Any,
    Callable,
    Iterable,
    Mapping,
)

import ctor
import aiohttp
from attr import dataclass

__all__ = [
    "DotaMatch",
    "Player",
    "DotaItem",
    "DotaItemAttrib",
    "PlayerRecentMatch",
    "get_items",
    "get_item_ids",
    "get_heroes",
    "translate_dota_rank",
    "get_player_recent_matches",
    "get_match",
]

DOTA_RANK_TIERS = ["I", "II", "III", "IV", "V"]
DOTA_RANK_NAMES = [
    "Herald",
    "Guardian",
    "Crusader",
    "Archon",
    "Legend",
    "Ancient",
    "Divine",
    "Immortal",
]


def translate_dota_rank(rank: int) -> str:
    dota_rank = DOTA_RANK_NAMES[(rank // 10) - 1]
    dota_tier = DOTA_RANK_TIERS[(rank % 10) - 1]
    return "{} {}".format(dota_rank, dota_tier)


@dataclass(slots=True, frozen=True)
class Hero:
    id: int
    name: str
    localized_name: str
    primary_attr: str
    attack_type: str
    roles: List[str]
    img: str
    icon: str
    base_health: int
    base_health_regen: float
    base_mana: int
    base_mana_regen: int
    base_armor: int
    base_mr: int
    base_attack_min: int
    base_attack_max: int
    base_str: int
    base_agi: int
    base_int: int
    str_gain: float
    agi_gain: float
    int_gain: float
    attack_range: int
    projectile_speed: int
    attack_rate: float
    base_attack_time: int
    attack_point: float
    move_speed: int
    legs: int
    day_vision: int
    night_vision: int

    @property
    def image_vert_url(self) -> str:
        return "https://steamcdn-a.akamaihd.net/apps/dota2/images/heroes/{}_vert.jpg".format(self.name[14:])

    @property
    def icon_url(self) -> str:
        return "https://steamcdn-a.akamaihd.net/apps/dota2/images/heroes/{}_icon.png".format(self.name[14:])


@dataclass(slots=True, frozen=True)
class ChatEvent:
    time: Optional[int]
    type: Optional[str]
    key: Optional[str]
    slot: Optional[int]
    player_slot: Optional[int]


@dataclass(slots=True, frozen=True)
class PlayerBuybackEvent:
    time: Optional[int]
    slot: Optional[int]
    type: Optional[Literal["buyback_log"]]
    player_slot: Optional[int]


@dataclass(slots=True, frozen=True)
class PermanentBuffState:
    permanent_buff: Optional[int]
    stack_count: Optional[int]


@dataclass(slots=True, frozen=True, repr=False)
class Player:
    match_id: Optional[int]
    player_slot: Optional[int]
    assists: Optional[int]
    deaths: Optional[int]
    denies: Optional[int]
    gold: Optional[int]
    gold_per_min: Optional[int]
    gold_spent: Optional[int]
    hero_damage: Optional[int]
    hero_healing: Optional[int]
    hero_id: Optional[int]
    item_0: Optional[int]
    item_1: Optional[int]
    item_2: Optional[int]
    item_3: Optional[int]
    item_4: Optional[int]
    item_5: Optional[int]
    item_neutral: Optional[int]
    kills: Optional[int]
    last_hits: Optional[int]
    leaver_status: Optional[int]
    level: Optional[int]
    tower_damage: Optional[int]
    xp_per_min: Optional[int]
    radiant_win: Optional[bool]
    start_time: Optional[int]
    duration: Optional[int]
    cluster: Optional[int]
    lobby_type: Optional[int]
    game_mode: Optional[int]
    patch: Optional[int]
    isRadiant: Optional[bool]
    win: Optional[int]
    lose: Optional[int]
    total_gold: Optional[int]
    total_xp: Optional[int]
    abandons: Optional[int]
    rank_tier: Optional[int]
    account_id: Optional[int] = None
    camps_stacked: Optional[int] = None
    creeps_stacked: Optional[int] = None
    damage: Optional[float] = None
    damage_taken: Optional[float] = None
    dn_t: Optional[List[int]] = None
    firstblood_claimed: Optional[int] = None
    net_worth: Optional[int] = None
    obs_placed: Optional[int] = None
    pred_vict: Optional[bool] = None
    randomed: Optional[bool] = None
    roshans_killed: Optional[int] = None
    rune_pickups: Optional[int] = None
    sen_placed: Optional[int] = None
    stuns: Optional[float] = None
    towers_killed: Optional[int] = None
    observer_uses: Optional[int] = None
    sentry_uses: Optional[int] = None
    item_win: Optional[Dict[str, int]] = None
    item_usage: Optional[Dict[str, int]] = None
    actions_per_min: Optional[int] = None
    life_state_dead: Optional[int] = None
    neutral_kills: Optional[int] = None
    kills_per_min: Optional[float] = None
    personaname: Optional[str] = None
    region: Optional[int] = None
    purchase_ward_observer: Optional[int] = None
    purchase_ward_sentry: Optional[int] = None
    purchase_tpscroll: Optional[int] = None
    pings: Optional[int] = None
    teamfight_participation: Optional[float] = None


GAME_MODES = [
    "Unknown",
    "All pick",
    "Captains mode",
    "Random draft",
    "Single draft",
    "All random",
    "Intro",
    "Diretide",
    "Reverse captains mode",
    "Greeviling",
    "Tutorial",
    "Mid only",
    "Least played",
    "Limited heroes",
    "Compendium matchmaking",
    "Custom",
    "Captains draft",
    "Balanced draft",
    "Ability draft",
    "Event",
    "All random death match",
    "1v1 mid",
    "All draft",
    "Turbo",
    "Mutation"
]


@dataclass(slots=True, frozen=True, repr=False)
class DotaMatch:
    match_id: int
    start_time: int
    game_mode: int
    barracks_status_dire: Optional[int]
    barracks_status_radiant: Optional[int]
    cluster: Optional[int]
    dire_score: Optional[int]
    duration: Optional[int]
    engine: Optional[int]
    first_blood_time: Optional[int]
    human_players: Optional[int]
    leagueid: Optional[int]
    lobby_type: Optional[int]
    match_seq_num: Optional[int]
    negative_votes: Optional[int]
    positive_votes: Optional[int]
    radiant_score: Optional[int]
    radiant_win: Optional[bool]
    tower_status_dire: Optional[int]
    tower_status_radiant: Optional[int]
    players: List[Player]
    patch: Optional[int]
    skill: Optional[int] = None
    version: Optional[int] = None
    dire_team_id: Optional[int] = None
    radiant_gold_adv: Optional[List[int]] = None
    radiant_team_id: Optional[int] = None
    radiant_xp_adv: Optional[List[int]] = None
    chat: Optional[List[ChatEvent]] = None
    replay_url: Optional[str] = None
    region: Optional[int] = None
    throw: Optional[int] = None
    loss: Optional[int] = None
    replay_salt: Optional[int] = None
    series_id: Optional[int] = None
    series_type: Optional[int] = None

    @property
    def start_date(self) -> str:
        return datetime.fromtimestamp(self.start_time).strftime('%d/%m/%Y')

    @property
    def game_mode_localized(self) -> str:
        return GAME_MODES[self.game_mode]

    @property
    def url(self) -> str:
        return f"https://www.opendota.com/matches/{self.match_id}"

    def find_player(self, account_id: int) -> Optional[Player]:
        for player in self.players:
            if player.account_id == account_id:
                return player
        return None


@dataclass(slots=True, frozen=True)
class PlayerRecentMatch:
    match_id: int
    player_slot: Optional[int]
    radiant_win: Optional[bool]
    duration: Optional[int]
    game_mode: Optional[int]
    lobby_type: Optional[int]
    hero_id: Optional[int]
    start_time: Optional[int]
    kills: Optional[int]
    deaths: Optional[int]
    assists: Optional[int]
    xp_per_min: Optional[int]
    gold_per_min: Optional[int]
    hero_damage: Optional[int]
    tower_damage: Optional[int]
    hero_healing: Optional[int]
    last_hits: Optional[int]
    cluster: Optional[int]
    leaver_status: Optional[int]
    lane: Optional[int] = None
    skill: Optional[int] = None
    version: Optional[int] = None
    lane_role: Optional[int] = None
    is_roaming: Optional[bool] = None
    party_size: Optional[int] = None


@dataclass(slots=True)
class DotaItemAttrib:
    key: str
    header: str
    value: Union[str, List[str]]
    footer: str = ""


@dataclass(slots=True)
class DotaItem:
    id: int
    img: str
    cost: Optional[int]
    notes: str
    attrib: List[DotaItemAttrib]
    mc: Union[bool, int]
    cd: int
    lore: str
    created: bool
    dname: str = ""
    qual: str = ""
    hint: Optional[List[str]] = None
    charges: Union[bool, int] = False
    components: Optional[List[str]] = None


class CacheWithLifetime:
    function: Callable[..., Any]

    _cache: Optional[Any] = None
    _cache_creation_time: float = -1.0
    _cache_lifetime: float = 60 * 60 * 24  # 24 hours

    def __init__(self, function: Callable[..., Any]) -> None:
        self.function = function

    def _cache_is_expired(self) -> bool:
        return self._cache_creation_time + self._cache_lifetime < time()

    async def __call__(self, *args: Iterable[Any], **kwargs: Mapping[str, Any]) -> Any:
        if not self._cache or self._cache_is_expired():
            self._cache = await self.function(*args, **kwargs)
            self._cache_creation_time = time()
        return self._cache


@CacheWithLifetime
async def get_items() -> Dict[str, DotaItem]:
    data = await get_json(
        "https://raw.githubusercontent.com/odota/dotaconstants/master/build/items.json"
    )
    return ctor.load(Dict[str, DotaItem], data)


@CacheWithLifetime
async def get_item_ids() -> Dict[str, str]:
    data = await get_json(
        "https://raw.githubusercontent.com/odota/dotaconstants/master/build/item_ids.json"
    )
    return ctor.load(Dict[str, str], data)


@CacheWithLifetime
async def get_permanent_buffs() -> Dict[str, str]:
    data = await get_json(
        "https://raw.githubusercontent.com/odota/dotaconstants/master/json/permanent_buffs.json"
    )
    return ctor.load(Dict[str, str], data)


@CacheWithLifetime
async def get_heroes() -> Dict[int, Hero]:
    data = await get_json(
        "https://raw.githubusercontent.com/odota/dotaconstants/master/build/heroes.json"
    )
    return {
        int(hero_id): ctor.load(Hero, hero_data) for hero_id, hero_data in data.items()
    }


async def get_json(url: str) -> Dict[str, Any]:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.read()
            return json.loads(data)


async def get_match(match_id: Union[str, int]) -> DotaMatch:
    data = await get_json(f"https://api.opendota.com/api/matches/{match_id}")
    return ctor.load(DotaMatch, data)


async def get_player_recent_matches(
    account_id: Union[str, int], limit: int = 10, significant: Literal[0, 1] = 0
) -> List[PlayerRecentMatch]:
    data = await get_json(
        f"https://api.opendota.com/api/players/{account_id}/recentMatches?limit={limit}&significant={significant}"
    )
    return ctor.load(List[PlayerRecentMatch], data)


async def main():
    await get_match(6862778480)


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
