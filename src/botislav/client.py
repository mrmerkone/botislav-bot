from logging import getLogger

from discord import Client, Message, Intents

from botislav.dialog import DialogManager

_logger = getLogger(__name__)


class BotislavClient(Client):
    def __init__(
        self,
        dialog_manager: DialogManager,
    ):
        intents = Intents.default()
        intents.message_content = True
        super(BotislavClient, self).__init__(intents=intents)
        self.dialog_manager: DialogManager = dialog_manager

    async def on_message(self, message: Message):

        if message.author == self.user:
            return

        await self.dialog_manager.handle(message)
