from discord import Client, Message, DMChannel

from botislav.commands import ActionManager
from botislav.common import Context


class BotislavClient(Client):
    def __init__(self, action_manager: ActionManager):
        super(BotislavClient, self).__init__()
        self.action_manager = action_manager

    async def on_message(self, message: Message):

        if message.author == self.user:
            return

        context = Context(message)

        if isinstance(message.channel, DMChannel):
            if action := self.action_manager.get_action(message.content):
                await action.run(context)
