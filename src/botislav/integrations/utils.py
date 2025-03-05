import json
from time import time
from typing import Callable, Any, Optional, Iterable, Mapping, Dict

import aiohttp


class CacheWithLifetime:
    function: Callable[..., Any]

    _cache: Optional[Any] = None
    _cache_creation_time: float = -1.0
    _cache_lifetime: float = 60 * 60 * 24  # 24 hours

    def __init__(self, function: Callable[..., Any]) -> None:
        self.function = function

    def _cache_is_expired(self) -> bool:
        return self._cache_creation_time + self._cache_lifetime < time()

    async def __call__(self, *args: Iterable[Any], **kwargs: Mapping[str, Any]) -> Any:
        if not self._cache or self._cache_is_expired():
            self._cache = await self.function(*args, **kwargs)
            self._cache_creation_time = time()
        return self._cache


async def get_json(url: str) -> Dict[str, Any]:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.read()
            return json.loads(data)