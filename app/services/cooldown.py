import time
import asyncio
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


class CooldownManager:
    def __init__(self, cooldown_seconds: int = 30):
        self.cooldown = cooldown_seconds
        self._store: dict[Tuple[int, int, str], float] = {}
        self._lock = asyncio.Lock()

    async def allow(self, group_id: int, user_id: int, keyword: str) -> bool:
        key = (group_id, user_id, keyword)
        now = time.time()
        async with self._lock:
            last = self._store.get(key)
            if last is None or (now - last) >= self.cooldown:
                self._store[key] = now
                return True
            return False

    async def prune(self, older_than: int = 300):
        now = time.time()
        async with self._lock:
            keys = [k for k, v in self._store.items() if (now - v) > older_than]
            for k in keys:
                del self._store[k]
