"""Store Factory for selecting backend based on configuration."""

from core.settings import settings
from core.logger import get_logger

logger = get_logger("store_factory")


def get_store_connection():
    """
    Get the appropriate store connection based on the BACKEND setting.
    
    Returns:
        Connection object (RedisConnection, PostgreSQLConnection, or MongoDBConnection)
        
    Raises:
        ValueError: If BACKEND is not one of: redis, postgresql, mongodb
    """
    backend = settings.BACKEND.lower()
    
    logger.info(f"Selecting store backend: {backend}")
    
    if backend == "redis":
        from database.redis_langgraph_client import redis_connection
        logger.debug("Using Redis store backend")
        return redis_connection
    elif backend == "postgresql":
        from database.postgresql_langgraph_client import postgresql_connection
        logger.debug("Using PostgreSQL store backend")
        return postgresql_connection
    elif backend == "mongodb":
        from database.mongodb_langgraph_client import mongodb_connection
        logger.debug("Using MongoDB store backend")
        return mongodb_connection
    else:
        error_msg = f"Invalid BACKEND setting: '{backend}'. Must be one of: redis, postgresql, mongodb"
        logger.error(error_msg)
        raise ValueError(error_msg)

