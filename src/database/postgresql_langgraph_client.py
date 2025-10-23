import os
import asyncio

from core.settings import settings
from core.logger import get_logger
from langgraph.store.postgres import AsyncPostgresStore
from contextlib import asynccontextmanager

logger = get_logger("postgresql_connection")

class PostgreSQLConnection:
    def __init__(self):
        self.settings = settings.postgresql
        self.postgres_url = self.settings.get_connection_string()
        os.environ["POSTGRES_URL"] = self.postgres_url
        logger.debug(f"Initializing PostgreSQL connection to {self.settings.HOST}:{self.settings.PORT}/{self.settings.DATABASE}")
        
        # Default TTL configuration
        self.ttl_config = None
        self._setup_done = False
        
    async def ensure_setup(self):
        """Ensure the store is set up (run migrations)."""
        if not self._setup_done:
            logger.info("Running PostgreSQL store setup (migrations)...")
            async with AsyncPostgresStore.from_conn_string(self.postgres_url) as store:
                await store.setup()
            self._setup_done = True
            logger.info("PostgreSQL store setup completed")
    
    @asynccontextmanager
    async def get_store(self, ttl_config: dict = None):
        """
        Returns a PostgreSQL store instance as a context manager.
        Automatically runs setup on first use.
        """
        await self.ensure_setup()
        
        ttl = ttl_config or self.ttl_config
        
        logger.debug("Returning PostgreSQL store with TTL config")
        async with AsyncPostgresStore.from_conn_string(self.postgres_url, ttl=ttl) as store:
            yield store


postgresql_connection = PostgreSQLConnection()

