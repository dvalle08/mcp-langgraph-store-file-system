import os
from pydantic import Field, field_validator
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
    
    # Memory Store Configuration
    ALLOWED_NAMESPACES: list[str] = Field(
        default_factory=list,
        description="List of allowed namespaces. Empty list means all namespaces are allowed."
    )
    READ_ONLY_FILES: list[str] = Field(
        default_factory=list,
        description="List of read-only files in format 'namespace/key'"
    )
    
    @field_validator('ALLOWED_NAMESPACES', 'READ_ONLY_FILES', mode='before')
    @classmethod
    def parse_comma_separated(cls, v):
        """Parse comma-separated string into list."""
        if isinstance(v, str):
            if not v.strip():
                return []
            return [item.strip() for item in v.split(',') if item.strip()]
        return v or []
    
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

