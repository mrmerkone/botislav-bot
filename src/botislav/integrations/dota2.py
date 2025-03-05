import ctor
from attr import dataclass

from botislav.integrations.utils import CacheWithLifetime, get_json


@dataclass
class Dota2Hero:
    id: int
    name: str
    order_id: int
    name_loc: str
    bio_loc: str
    hype_loc: str
    npe_desc_loc: str
    str_base: float
    str_gain: float
    agi_base: float
    agi_gain: float
    int_base: float
    int_gain: float
    primary_attr: int
    complexity: int
    attack_capability: int
    damage_min: float
    damage_max: float
    attack_rate: float
    attack_range: int
    projectile_speed: int
    armor: float
    magic_resistance: int
    movement_speed: int
    turn_rate: float
    sight_range_day: int
    sight_range_night: int
    max_health: int
    health_regen: float
    max_mana: int
    mana_regen: float


@CacheWithLifetime
async def get_hero_info_from_dota2_com(hero_id: int) -> Dota2Hero:
    data = await get_json(
        f"https://www.dota2.com/datafeed/herodata?language=russian&hero_id={hero_id}"
    )
    hero_data = next(iter(data["result"]["data"]["heroes"]))
    return ctor.load(Dota2Hero, hero_data)