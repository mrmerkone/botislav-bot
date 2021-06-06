from discord import Client, Message, DMChannel

from intent import IntentMatcher


class BotislavBot(Client):

    def __init__(self, intent_matcher: IntentMatcher):
        super(BotislavBot, self).__init__()
        self.intent_matcher = intent_matcher

    async def on_message(self, message: Message):

        if message.author == self.user:
            return

        if isinstance(message.channel, DMChannel):
            intent = await self.intent_matcher.match(message.content)
            if intent:
                await message.channel.send(intent)
