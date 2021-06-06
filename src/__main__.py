import logging
import pathlib

import discord

from intents import create_intent_matcher, IntentMatcher

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


class BotislavBot(discord.Client):

    def __init__(self, intent_matcher: IntentMatcher):
        super(BotislavBot, self).__init__()
        self.intent_matcher = intent_matcher

    async def on_message(self, message: discord.Message):

        if message.author == self.user:
            return

        if isinstance(message.channel, discord.DMChannel):
            intent = self.intent_matcher.match(message.content)
            if intent:
                await message.channel.send(intent)


if __name__ == '__main__':
    intent_paths = list(pathlib.Path("../resources/intents/").glob("*.y*ml"))
    bot = BotislavBot(
        intent_matcher=create_intent_matcher(intent_paths)
    )
    bot.run("token")