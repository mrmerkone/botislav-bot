import asyncio
import logging
from typing import Dict

import discord
from attr import dataclass, attrib

from botislav.context import BotContext, BotContextManager
from botislav.handlers import Handler
from botislav.intents import IntentClassifier

_logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class Dialog:
    task: asyncio.Task
    context: BotContext

    def is_active(self) -> bool:
        return not self.task.done()

    def resume(self, discord_message: discord.Message) -> None:
        self.context.set_user_reply(discord_message)


@dataclass(slots=True)
class DialogManager:
    intent_classifier: IntentClassifier
    context_manager: BotContextManager
    handlers: Dict[str, Handler] = attrib(factory=dict)
    active_dialogs: Dict[str, Dialog] = attrib(factory=dict)

    async def handle(self, message: discord.Message) -> None:
        self.active_dialogs = {
            key: dialog
            for key, dialog in self.active_dialogs.items()
            if dialog.is_active()
        }

        context = self.context_manager.get_context_from(message)

        if context.key in self.active_dialogs:
            _logger.info(f"Resuming dialog for {context.key}")
            self.active_dialogs[context.key].resume(message)
            return

        _logger.info(f"Starting new dialog for {context.key}")
        intent = self.intent_classifier.get_intent(message.content)
        handler = self.handlers[intent.handler_id]
        task = asyncio.create_task(handler(context))
        self.active_dialogs[context.key] = Dialog(task, context)
