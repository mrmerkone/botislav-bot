from logging import getLogger
from typing import Dict

from discord import Client, Message, DMChannel, Intents

from botislav.phrases import PhraseMetaExtractor
from botislav.context import ContextManager
from botislav.handlers import Handler

_logger = getLogger(__name__)


class BotislavClient(Client):
    def __init__(
        self,
        phrase_meta_extractor: PhraseMetaExtractor,
        context_manager: ContextManager,
        handlers: Dict[str, Handler],
    ):
        intents = Intents.default()
        intents.message_content = True
        super(BotislavClient, self).__init__(intents=intents)
        self.phrase_meta_extractor = phrase_meta_extractor
        self.context_manager = context_manager
        self.handlers = handlers

    async def on_message(self, message: Message):

        if message.author == self.user:
            return

        # if isinstance(message.channel, DMChannel):
        phrase_meta = self.phrase_meta_extractor.extract(message.content)
        handler = self.handlers[phrase_meta.handler_id]
        with self.context_manager.get_context_from(
            client=self, message=message, phrase_meta=phrase_meta
        ) as context:
            _logger.info(f"Handling phrase with {handler.__class__.__name__}")
            await handler.handle(context)
