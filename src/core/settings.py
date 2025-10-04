import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class RedisSettings(BaseSettings):
    """Redis connection settings."""
    
    HOST: str = Field(default="localhost", description="Redis host")
    PORT: int = Field(default=6379, description="Redis port")
    PASSWORD: str = Field(default="", description="Redis password")
    DB: int = Field(default=0, description="Redis database number")
    
    model_config = SettingsConfigDict(
        env_prefix="REDIS_",
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


class Settings(BaseSettings):
    """Application settings."""
    
    # Environment
    ENVIRONMENT: str = Field(default="development", description="Application environment")
    DEBUG: bool = Field(default=True, description="Debug mode")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    
    # Redis configuration
    redis: RedisSettings = Field(default_factory=RedisSettings)
    
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize nested settings
        self.redis = RedisSettings()


# Global settings instance
settings = Settings()

