import asyncio
import logging
from typing import Dict

import discord
from attr import dataclass, attrib

from botislav.context import ContextManager
from botislav.handlers import Handler
from botislav.intents import IntentClassifier

_logger = logging.getLogger(__name__)


@dataclass(slots=True)
class DialogManager:
    context_manager: ContextManager
    intent_classifier: IntentClassifier
    handlers: Dict[str, Handler] = attrib(factory=dict)
    client: discord.Client = attrib(init=False)

    def set_client(self, client: discord.Client):
        self.client = client

    async def _start_dialog(self, key: str, message: discord.Message):
        phrase = message.content.lower()
        intent = self.intent_classifier.get_intent(phrase)
        handler = self.handlers[intent.handler_id]
        with self.context_manager.get_context(key, message) as context:
            await handler(context)
        _logger.info(f"Dialog {key} ended")

    async def handle(self, message: discord.Message) -> None:
        key = str(message.author.id)

        if self.context_manager.has_active_context(key):
            _logger.info(f"Resuming dialog for {key}")
            self.context_manager.pass_reply_to_active_context(key, message)
        else:
            _logger.info(f"Starting new dialog for {key}")
            asyncio.create_task(self._start_dialog(key, message))
