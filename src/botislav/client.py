from discord import Client, Message, DMChannel

from botislav.parsing import PhraseParser


class BotislavClient(Client):
    def __init__(self, parser: PhraseParser):
        super(BotislavClient, self).__init__()
        self.parser = parser

    async def on_message(self, message: Message):

        if message.author == self.user:
            return

        if isinstance(message.channel, DMChannel):
            if action := self.parser.parse(message.content):
                await action.reply(message)
