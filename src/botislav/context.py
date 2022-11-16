from typing import Dict, Any

from attr import dataclass
from discord import Message


@dataclass
class Context:
    message: Message



class Action(object):
    pass
