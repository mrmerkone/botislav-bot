import json
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
from functools import cache
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


@dataclass(slots=True, frozen=True)
class ChatEvent:
    time: int
    type: str
    key: str
    slot: int
    player_slot: int


@dataclass(slots=True, frozen=True)
class PlayerBuybackEvent:
    time: int
    slot: int
    type: Literal["buyback_log"]
    player_slot: int


@dataclass(slots=True, frozen=True)
class PermanentBuffState:
    permanent_buff: int
    stack_count: int


@dataclass(slots=True, frozen=True, repr=False)
class Player:
    match_id: int
    player_slot: int
    account_id: Optional[int]
    assists: int
    buyback_log: Optional[List[PlayerBuybackEvent]]
    camps_stacked: Optional[int]
    creeps_stacked: Optional[int]
    damage: Optional[float]
    damage_taken: Optional[float]
    deaths: int
    denies: int
    dn_t: Optional[List[int]]
    firstblood_claimed: Optional[int]
    gold: int
    gold_per_min: int
    gold_spent: int
    hero_damage: int
    hero_healing: int
    hero_id: int
    item_0: int
    item_1: int
    item_2: int
    item_3: int
    item_4: int
    item_5: int
    item_neutral: int
    kills: int
    last_hits: int
    leaver_status: int
    level: int
    net_worth: Optional[int]
    obs_placed: Optional[int]
    permanent_buffs: Optional[List[PermanentBuffState]]
    pred_vict: Optional[bool]
    randomed: Optional[bool]
    roshans_killed: Optional[int]
    rune_pickups: Optional[int]
    sen_placed: Optional[int]
    stuns: Optional[float]
    teamfight_participation: Optional[float]
    tower_damage: int
    towers_killed: Optional[int]
    xp_per_min: int
    radiant_win: bool
    start_time: int
    duration: int
    cluster: int
    lobby_type: int
    game_mode: int
    patch: int
    isRadiant: bool
    win: int
    lose: int
    total_gold: int
    total_xp: int
    abandons: int
    rank_tier: Optional[int]
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


@dataclass(slots=True, frozen=True, repr=False)
class DotaMatch:
    match_id: int
    barracks_status_dire: int
    barracks_status_radiant: int
    chat: Optional[List[ChatEvent]]
    cluster: int
    dire_score: int
    dire_team_id: Optional[int]
    duration: int
    engine: int
    first_blood_time: int
    game_mode: int
    human_players: int
    leagueid: int
    lobby_type: int
    match_seq_num: int
    negative_votes: int
    positive_votes: int
    radiant_gold_adv: Optional[List[int]]
    radiant_score: int
    radiant_team_id: Optional[int]
    radiant_win: bool
    radiant_xp_adv: Optional[List[int]]
    skill: Optional[int]
    start_time: int
    tower_status_dire: int
    tower_status_radiant: int
    version: Optional[int]
    players: List[Player]
    patch: int
    replay_url: Optional[str] = None
    region: Optional[int] = None
    throw: Optional[int] = None
    loss: Optional[int] = None
    replay_salt: Optional[int] = None
    series_id: Optional[int] = None
    series_type: Optional[int] = None

    @property
    def url(self) -> str:
        return f"https://www.opendota.com/matches/{self.match_id}"


@dataclass(slots=True, frozen=True)
class PlayerRecentMatch:
    match_id: int
    player_slot: int
    radiant_win: bool
    duration: int
    game_mode: int
    lobby_type: int
    hero_id: int
    start_time: int
    version: Optional[int]
    kills: int
    deaths: int
    assists: int
    skill: Optional[int]
    xp_per_min: int
    gold_per_min: int
    hero_damage: int
    tower_damage: int
    hero_healing: int
    last_hits: int
    lane: Optional[int]
    lane_role: Optional[int]
    is_roaming: Optional[bool]
    cluster: int
    leaver_status: int
    party_size: Optional[int]


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
    components: Optional[List[str]]
    created: bool
    dname: str = ""
    qual: str = ""
    hint: Optional[List[str]] = None
    charges: Union[bool, int] = False


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
async def get_heroes() -> Dict[str, Hero]:
    data = await get_json(
        "https://raw.githubusercontent.com/odota/dotaconstants/master/build/heroes.json"
    )
    return ctor.load(Dict[str, Hero], data)


async def get_json(url: str) -> Any:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.read()
            return json.loads(data)


@CacheWithLifetime
async def get_match(match_id: Union[str, int]) -> DotaMatch:
    data = await get_json(f"https://api.opendota.com/api/matches/{match_id}")
    return ctor.load(DotaMatch, data)


async def get_player_recent_matches(
    account_id: Union[str, int], limit: int = 10
) -> List[PlayerRecentMatch]:
    data = await get_json(
        f"https://api.opendota.com/api/players/{account_id}/recentMatches?limit={limit}"
    )
    return ctor.load(List[PlayerRecentMatch], data)
