from lark import Transformer

from botislav.common import Action, Context

__all__ = ["GreetingAction", "GreetingTransformer"]


class GreetingAction(Action):
    async def run(self, context: Context):
        await context.message.channel.send("здарова")


class GreetingTransformer(Transformer):
    # noinspection PyMethodMayBeStatic
    def greeting(self, _):
        return GreetingAction()
