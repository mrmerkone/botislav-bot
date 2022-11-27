import asyncio
from typing import Dict

import discord
from attr import dataclass, attrib

from botislav.context import BotContext, BotContextManager
from botislav.handlers import Handler
from botislav.intents import IntentClassifier


@dataclass(slots=True)
class Dialog:
    task: asyncio.Task
    context: BotContext

    def is_active(self) -> bool:
        return not self.task.done()

    def resume(self, discord_message: discord.Message):
        self.context.resume(discord_message)


@dataclass(slots=True)
class DialogManager:
    intent_classifier: IntentClassifier
    context_manager: BotContextManager
    handlers: Dict[str, Handler] = attrib(factory=dict)
    active_dialogs: Dict[str, Dialog] = attrib(factory=dict)

    async def handle(self, message: discord.Message):
        self.active_dialogs = {
            user_key: dialog
            for user_key, dialog in self.active_dialogs.items()
            if dialog.is_active()
        }

        user_key = str(message.author.id)

        if user_key in self.active_dialogs:
            self.active_dialogs[user_key].resume(message)
            return

        context = self.context_manager.get_context_from(message)
        intent = self.intent_classifier.get_intent(message.content)
        handler = self.handlers[intent.handler_id]
        task = asyncio.create_task(handler(context))

        self.active_dialogs[user_key] = Dialog(task, context)
