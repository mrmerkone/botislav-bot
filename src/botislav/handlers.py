import re
from typing import Dict, Callable, Awaitable

from botislav.context import Context
from botislav.opendota import get_player_recent_matches, get_match, get_heroes

__all__ = [
    "Handler",
    "get_handlers",
]

Handler = Callable[[Context], Awaitable[None]]


OPENDOTA_ID_PATTERN = re.compile(
    r"^(https://www.)?opendota.com/players/(?P<opendota_id>\d+)$"
)


async def pubg_lastmatch(context: Context) -> None:
    await context.reply_to_user("Ты что играешь в БАБАДЖИ ???")


async def ensure_user_has_linked_opendota(context: Context) -> None:

    if context.cache.opendota_id:
        return

    await context.reply_to_user("Дай ссылку на профиль в https://www.opendota.com")
    replied = await context.wait_for_user_reply(timeout=60)

    if not replied:
        return

    if match := OPENDOTA_ID_PATTERN.match(context.user_text):
        context.cache.opendota_id = int(match.groupdict().get("opendota_id"))
        await context.reply_to_user("Привязал к тебе этот профиль")


async def dota_lastmatch(context: Context) -> None:

    await ensure_user_has_linked_opendota(context)

    opendota_id = context.cache.opendota_id

    if not opendota_id:
        await context.reply_to_user("Не могу продолжить, не зная твоего профиля")
        return

    recent_matches = await get_player_recent_matches(account_id=opendota_id, limit=1)

    if recent_match := next(iter(recent_matches), None):
        match = await get_match(recent_match.match_id)
        if player := match.find_player(opendota_id):
            heroes = await get_heroes()
            player_hero = heroes[player.hero_id]
            await context.reply_to_user(
                f"Ты {'выйграл' if player.win else 'проиграл'} на {player_hero.localized_name} со счетом "
                f"{player.kills}/{player.deaths}/{player.assists} "
                f"{match.url}"
            )


async def greeting(context: Context) -> None:
    await context.reply_to_user("Здарова")


async def silence(_context: Context) -> None:
    pass


def get_handlers() -> Dict[str, Handler]:
    return {
        "dota_lastmatch": dota_lastmatch,
        "pubg_lastmatch": pubg_lastmatch,
        "greeting": greeting,
        "silence": silence,
    }
