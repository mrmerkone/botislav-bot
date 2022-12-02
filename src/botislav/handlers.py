import re
from typing import Dict, Callable, Awaitable

from botislav.context import BotContext
from botislav.opendota import get_player_recent_matches, get_match, get_heroes

__all__ = [
    "Handler",
    "get_handlers",
]

Handler = Callable[[BotContext], Awaitable[None]]


OPENDOTA_ID_PATTERN = re.compile(
    r"^(https://www.)?opendota.com/players/(?P<opendota_id>\d+)$"
)


async def pubg_lastmatch(context: BotContext) -> None:
    await context.reply_to_user("Ты что играешь в БАБАДЖИ ???")


async def ensure_user_has_linked_opendota(context: BotContext) -> None:

    await context.reply_to_user("Дай ссылку на профиль в https://www.opendota.com")
    replied = await context.wait_for_user_reply(seconds=60)

    if not replied:
        return

    if match := OPENDOTA_ID_PATTERN.match(context.user_text):
        user_cache = context.get_cache()
        user_cache.opendota_id = int(match.groupdict().get("opendota_id"))
        await context.reply_to_user("Привязал к тебе этот профиль")
        context.set_cache(user_cache)


async def dota_lastmatch(context: BotContext) -> None:

    user_cache = context.get_cache()
    if not user_cache.opendota_id:
        await ensure_user_has_linked_opendota(context)

    recent_matches = await get_player_recent_matches(
        account_id=user_cache.opendota_id, limit=1
    )

    if recent_match := next(iter(recent_matches), None):
        match = await get_match(recent_match.match_id)
        player = next(
            filter(lambda p: p.account_id == user_cache.opendota_id, match.players)
        )
        hero = (await get_heroes())[str(player.hero_id)]
        await context.reply_to_user(
            f"Ты {'выйграл' if player.win else 'проиграл'} на {hero.localized_name} со счетом "
            f"{player.kills}/{player.deaths}/{player.assists} "
            f"{match.url}"
        )


async def greeting(context: BotContext) -> None:
    await context.reply_to_user("Здарова")


async def silence(_context: BotContext) -> None:
    pass


def get_handlers() -> Dict[str, Handler]:
    return {
        "dota_lastmatch": dota_lastmatch,
        "pubg_lastmatch": pubg_lastmatch,
        "greeting": greeting,
        "silence": silence,
    }
