# services/api/core/cache.py
import json
import time
import os
from abc import ABC, abstractmethod
from typing import Any, Optional, Callable
from functools import wraps
from .logging import get_logger

logger = get_logger("cache")

class CachePort(ABC):
    """Abstract interface (port) for caching layer."""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        pass
        
    @abstractmethod
    async def setex(self, key: str, ttl: int, value: Any) -> None:
        pass
        
    @abstractmethod
    async def delete(self, key: str) -> None:
        pass

    @abstractmethod
    async def clear_pattern(self, pattern: str) -> None:
        pass

class InMemoryCache(CachePort):
    """In-memory cache with TTL support for development / fallback."""
    def __init__(self):
        self._store: dict[str, tuple[Any, float]] = {}

    async def get(self, key: str) -> Optional[Any]:
        if key in self._store:
            val, expiry = self._store[key]
            if time.time() < expiry:
                return val
            del self._store[key]
        return None

    async def setex(self, key: str, ttl: int, value: Any) -> None:
        self._store[key] = (value, time.time() + ttl)

    async def delete(self, key: str) -> None:
        self._store.pop(key, None)

    async def clear_pattern(self, pattern: str) -> None:
        prefix = pattern.rstrip("*")
        keys_to_del = [k for k in self._store.keys() if k.startswith(prefix)]
        for k in keys_to_del:
            self._store.pop(k, None)

class RedisCache(CachePort):
    """Production Redis caching implementation."""
    def __init__(self, url: str):
        try:
            import redis.asyncio as aioredis
            self._client = aioredis.from_url(url, decode_responses=True)
            self._available = True
        except Exception as e:
            logger.warning(f"Redis initialization failed: {e}. Falling back to InMemoryCache.")
            self._fallback = InMemoryCache()
            self._available = False

    async def get(self, key: str) -> Optional[Any]:
        if not self._available:
            return await self._fallback.get(key)
        try:
            raw = await self._client.get(key)
            return json.loads(raw) if raw else None
        except Exception as e:
            logger.warning(f"Redis get error: {e}")
            return None

    async def setex(self, key: str, ttl: int, value: Any) -> None:
        if not self._available:
            return await self._fallback.setex(key, ttl, value)
        try:
            await self._client.setex(key, ttl, json.dumps(value))
        except Exception as e:
            logger.warning(f"Redis setex error: {e}")

    async def delete(self, key: str) -> None:
        if not self._available:
            return await self._fallback.delete(key)
        try:
            await self._client.delete(key)
        except Exception as e:
            logger.warning(f"Redis delete error: {e}")

    async def clear_pattern(self, pattern: str) -> None:
        if not self._available:
            return await self._fallback.clear_pattern(pattern)
        try:
            keys = await self._client.keys(pattern)
            if keys:
                await self._client.delete(*keys)
        except Exception as e:
            logger.warning(f"Redis clear_pattern error: {e}")

# Global cache instance factory
_global_cache: Optional[CachePort] = None

def get_cache() -> CachePort:
    """Singleton getter for the application cache."""
    global _global_cache
    if _global_cache is None:
        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            _global_cache = RedisCache(redis_url)
        else:
            _global_cache = InMemoryCache()
    return _global_cache
