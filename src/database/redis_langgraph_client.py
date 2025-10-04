import asyncio
import os

from src.core.settings import settings
from src.core.logger import get_logger
from langgraph.store.redis.aio import AsyncRedisStore

logger = get_logger("redis_connection")

class RedisConnection:
    def __init__(self):
        self.settings = settings.redis
        self.redis_url = f"redis://:{settings.redis.PASSWORD}@{settings.redis.HOST}:{settings.redis.PORT}/{settings.redis.DB}"
        os.environ["REDIS_URL"] = self.redis_url
        logger.debug(f"Initializing Redis connection to {self.settings.HOST}:{self.settings.PORT}")
        
        # Default TTL configuration
        self.ttl_config =None
        # {
        #     "default_ttl": 120,  # Default TTL in minutes
        #     "refresh_on_read": True,  # Refresh TTL when store entries are read
        # }
    
    def get_store(self, ttl_config: dict = None):
        """
        Returns a sync or async Redis store instance.
        The returned object should be used as a context manager.
        """
        ttl = ttl_config or self.ttl_config
        
        logger.debug("Returning Async Redis store with TTL config")
        return AsyncRedisStore.from_conn_string(self.redis_url, ttl=ttl)


redis_connection = RedisConnection()
