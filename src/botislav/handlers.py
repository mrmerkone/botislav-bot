import re
import logging
from typing import Dict, Callable, Awaitable

from botislav.context import Context
from botislav.phrases import PHRASE_GENERATOR
from botislav.opendota import get_player_recent_matches, get_match, get_heroes

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
async def pubg_lastmatch(context: Context) -> None:
    await context.reply_to_user("Ты что играешь в БАБАДЖИ ???")


@handles_exceptions
async def link_account(context: Context) -> None:
    if match := OPENDOTA_ID_PATTERN.search(context.user_text):
        groups = match.groupdict()
        context.cache.opendota_id = int(groups["opendota_id"])
        await context.reply_to_user("Привязал к тебе этот профиль OpenDota")
        await context.add_reaction(context.normalize_emoji("FeelsGood"))


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

    recent_matches = await get_player_recent_matches(account_id=opendota_id, limit=1)
    recent_match = next(iter(recent_matches), None)

    if not recent_match:
        await context.reply_to_user("Не могу найти твой последний матч")
        return

    match = await get_match(recent_match.match_id)
    if player := match.find_player(opendota_id):
        hero = (await get_heroes())[player.hero_id]
        phrase = PHRASE_GENERATOR.get_phrase(
            win=player.win,
            username=player.personaname,
            hero=hero.localized_name,
            score="{}/{}/{}".format(player.kills, player.deaths, player.assists)
        )
        await context.reply_to_user_with_embed(
            title="{} {}".format(match.start_date, match.game_mode_localized),
            description="{}\n\n[OpenDota] {}".format(phrase, match.url),
            color=0x00a0ea,
            thumbnail=hero.image_vert_url
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
        "pubg_lastmatch": pubg_lastmatch,
        "greeting": greeting,
        "silence": silence,
    }
