import os

from core.settings import settings
from core.logger import get_logger
from langgraph.store.mongodb import MongoDBStore
from pymongo import MongoClient
from contextlib import asynccontextmanager

logger = get_logger("mongodb_connection")

class MongoDBConnection:
    def __init__(self):
        self.settings = settings.mongodb
        self.mongodb_uri = self.settings.URI
        self.database_name = self.settings.DATABASE
        self.collection_name = self.settings.COLLECTION
        os.environ["MONGODB_URI"] = self.mongodb_uri
        logger.debug(f"Initializing MongoDB connection to {self.mongodb_uri}")
        
        # Default TTL configuration
        self.ttl_config = None
        self._setup_done = False
        self._client = None
        
    async def ensure_setup(self):
        """Ensure the store is set up (run any necessary initialization)."""
        if not self._setup_done:
            logger.info("Running MongoDB store setup...")
            # MongoDB store may have a setup method, call it if available
            if self._client is None:
                self._client = MongoClient(self.mongodb_uri)
            db = self._client[self.database_name]
            collection = db[self.collection_name]
            store = MongoDBStore(collection=collection)
            if hasattr(store, 'setup'):
                await store.setup()
            self._setup_done = True
            logger.info("MongoDB store setup completed")
    
    @asynccontextmanager
    async def get_store(self, ttl_config: dict = None):
        """
        Returns a MongoDB store instance as a context manager.
        Automatically runs setup on first use.
        """
        await self.ensure_setup()
        
        ttl = ttl_config or self.ttl_config
        
        logger.debug(f"Returning MongoDB store for database: {self.database_name}, collection: {self.collection_name}")
        
        # Create MongoDB client if not exists
        if self._client is None:
            self._client = MongoClient(self.mongodb_uri)
        db = self._client[self.database_name]
        collection = db[self.collection_name]
        
        store = MongoDBStore(collection=collection, ttl=ttl)
        try:
            yield store
        finally:
            # MongoDB store doesn't need explicit cleanup in context manager
            pass


mongodb_connection = MongoDBConnection()

