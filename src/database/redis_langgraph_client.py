import asyncio
import os

from core.settings import settings
from core.logger import get_logger
from langgraph.store.redis.aio import AsyncRedisStore
from contextlib import asynccontextmanager

logger = get_logger("redis_connection")

class RedisConnection:
    def __init__(self):
        self.settings = settings.redis
        self.redis_url = f"redis://:{settings.redis.PASSWORD}@{settings.redis.HOST}:{settings.redis.PORT}/{settings.redis.DB}"
        os.environ["REDIS_URL"] = self.redis_url
        logger.debug(f"Initializing Redis connection to {self.settings.HOST}:{self.settings.PORT}")
        
        # Default TTL configuration
        self.ttl_config = None
        self._setup_done = False
        
    async def ensure_setup(self):
        """Ensure the store is set up (run any necessary initialization)."""
        if not self._setup_done:
            logger.info("Running Redis store setup...")
            async with AsyncRedisStore.from_conn_string(self.redis_url) as store:
                # Redis store may have a setup method, call it if available
                if hasattr(store, 'setup'):
                    await store.setup()
            self._setup_done = True
            logger.info("Redis store setup completed")
    
    @asynccontextmanager
    async def get_store(self, ttl_config: dict = None):
        """
        Returns an async Redis store instance as a context manager.
        Automatically runs setup on first use.
        """
        await self.ensure_setup()
        
        ttl = ttl_config or self.ttl_config
        
        logger.debug("Returning Async Redis store with TTL config")
        async with AsyncRedisStore.from_conn_string(self.redis_url, ttl=ttl) as store:
            yield store


redis_connection = RedisConnection()
