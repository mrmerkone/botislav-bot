import os
import re
import logging
from typing import Dict, Callable, Awaitable, TypedDict, Optional

from attr import dataclass
from langchain_gigachat import GigaChat
from langchain_core.prompts import PromptTemplate

from botislav.context import Context
from botislav.integrations.dota2 import get_hero_info_from_dota2_com
from botislav.integrations.opendota import get_player_recent_matches, get_match, get_heroes

_logger = logging.getLogger(__name__)

__all__ = [
    "Handler",
    "get_handlers",
]


Handler = Callable[[Context], Awaitable[None]]


OPENDOTA_ID_PATTERN = re.compile(
    r"(https?://)?(www\.)?opendota\.com/players/(?P<opendota_id>\d+)"
)


def handles_exceptions(func):
    async def wrapped(context: Context):
        try:
            return await func(context)
        except Exception as error:
            _logger.error(f"Handler {func.__qualname__} failed with {error}", exc_info=True)
            await context.reply_to_user("Упсс... кажется я сломался ...")
    return wrapped


@handles_exceptions
async def link_account(context: Context) -> None:
    if match := OPENDOTA_ID_PATTERN.search(context.user_text):
        groups = match.groupdict()
        context.cache.opendota_id = int(groups["opendota_id"])
        await context.reply_to_user("Привязал к тебе этот профиль OpenDota")
        await context.add_reaction(context.normalize_emoji("FeelsGood"))


giga = GigaChat(
    credentials=os.getenv("GIGACHAT_TOKEN"),
    model="GigaChat-Max",
    scope="GIGACHAT_API_PERS",
    verify_ssl_certs=False,
    max_tokens=100,
    top_p=0.5
)


PhrasePrompt = PromptTemplate.from_template("""
--- Задача ---
Опиши последний матч в Dota 2 игрока! Обязятельно делай отсылки на способности HERO_NAME!

--- Вывод ---
Будь ироничен и подшучивай над игроком! Обязательно шути! Твой текст не должен быть длинее 2 предложений!
Если Игрок выйграл и у него хороший счет восхваляй его используя самые сложные эпитеты!
Если Игрок выйграл и у него плохой счет шути что его затащила команда!
Если игорок проиграл и у него плохой счет смейся над ним что он якорь и бесполезный!
Если игорок проиграл и у него хороший счет пожалей его чтобы не было так обидно!
Твой текст должен быть от мужского рода.

--- Требования ---
HERO_NAME, NICKNAME и KDA из секции информации о матче обязяательно длжны быть в твоем ответе! Выделяй их **!

--- Контекст ---
Роль:
    HERO_NAME - {hero_name}
    HERO_DESCRIPTION - {hero_description}

Информация о матче:
    NICKNAME - {nickname}
    WIN - {win}
    KDA (Убийсвта/Смерти/Ассистов) - {kda}

Примеры:
  **Infighter** залил соляры на **Ogre Magi** со счетом **3/2/22**, выиграв пару раз вы казино
  **Kēksiņš** затащил на **Silencer** со счетом **6/9/22**, обезмолвив всех врагов
  **Fesh** показал всем, что у него большой RP на **Magnus** и выиграл со счетом **9/5/20**
  **Sanya** пытался победить на **Ursa** со счетом **4/7/11**, но его когти похоже сточились
  **JunkTapes** собрался на **Lion** и одержал победу со счетом **1/10/15**, заставив противников содрогнуться от страха
  **Kēksiņš** украл у противника все тайны, в том числе и победу на **Rubick**, счет **3/7/20**
  **Infighter** вызвал помощь из параллельных миров на **Enigma** со счетом **5/14/27**
""")

phrase_generator = PhrasePrompt | giga


@dataclass
class DotaRecentMatch:
    win: bool
    kda: str
    nickname: str
    hero_name: str
    hero_description: str
    hero_image_url: str
    date: str
    game_mode: str
    url: str

    def to_giga(self) -> Dict[str, str]:
        return {
            "win": self.win,
            "hero_name": self.hero_name,
            "hero_description": self.hero_description,
            "kda": self.kda,
            "nickname": self.nickname
        }


async def get_recent_match_info(opendota_account_id: int) -> Optional[DotaRecentMatch]:
    recent_matches = await get_player_recent_matches(account_id=opendota_account_id, limit=1)
    if recent_match := next(iter(recent_matches), None):
        full_match = await get_match(recent_match.match_id)
        if player := full_match.find_player(opendota_account_id):
            hero_from_dota2_com = await get_hero_info_from_dota2_com(hero_id=player.hero_id)
            hero_from_opendota = (await get_heroes())[player.hero_id]
            return DotaRecentMatch(
                win=bool(player.win),
                hero_name=hero_from_dota2_com.name_loc,
                hero_description=hero_from_dota2_com.hype_loc,
                kda="{}/{}/{}".format(player.kills, player.deaths, player.assists),
                date=full_match.start_date,
                nickname=player.personaname,
                hero_image_url=hero_from_opendota.image_vert_url,
                url=full_match.url,
                game_mode=full_match.game_mode_localized
            )
    return None


@handles_exceptions
async def dota_lastmatch(context: Context) -> None:

    if not context.cache.opendota_id:

        await context.reply_to_user("Дай ссылку на профиль в https://www.opendota.com")
        replied = await context.wait_for_user_reply(timeout=60)

        if not replied:
            return

        await link_account(context)

    opendota_id = context.cache.opendota_id
    if not opendota_id:
        await context.reply_to_user("Не могу найти матч, не зная твоего профиля")
        return

    match = await get_recent_match_info(opendota_account_id=opendota_id)

    if not match:
        await context.reply_to_user("Не могу найти твой последний матч")
        return

    giga_response = phrase_generator.invoke(match.to_giga())
    emoji = context.normalize_emoji("clueless") if match.win else context.normalize_emoji("aware")
    await context.reply_to_user_with_embed(
        title="{} {} {}".format(match.date, match.game_mode, emoji),
        description="{}\n\n[OpenDota] {}".format(giga_response.content, match.url),
        color=0x00a0ea,
        thumbnail=match.hero_image_url
    )


@handles_exceptions
async def greeting(context: Context) -> None:
    await context.reply_to_user("Здарова")


@handles_exceptions
async def silence(_context: Context) -> None:
    pass


def get_handlers() -> Dict[str, Handler]:
    return {
        "link_account": link_account,
        "dota_lastmatch": dota_lastmatch,
        "silence": silence,
    }
