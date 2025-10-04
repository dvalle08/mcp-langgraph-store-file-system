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
    
    # MCP Server Configuration
    TRANSPORT: str = Field(
        default="stdio",
        description="MCP transport mode: 'stdio' or 'streamable-http'"
    )
    HOST: str = Field(default="0.0.0.0", description="HTTP server host (for streamable-http)")
    PORT: int = Field(default=8000, description="HTTP server port (for streamable-http)")
    
    # Redis configuration
    redis: RedisSettings = Field(default_factory=RedisSettings)
    
    # Memory Store Configuration
    ALLOWED_NAMESPACES: str = Field(
        default="",
        description="Comma-separated list of allowed namespaces. Empty means all namespaces are allowed."
    )
    READ_ONLY_FILES: str = Field(
        default="",
        description="Comma-separated list of read-only files in format 'namespace/key'"
    )
    
    def get_allowed_namespaces(self) -> list[str]:
        """Get list of allowed namespaces from comma-separated string."""
        if not self.ALLOWED_NAMESPACES or not self.ALLOWED_NAMESPACES.strip():
            return []
        return [item.strip() for item in self.ALLOWED_NAMESPACES.split(',') if item.strip()]
    
    def get_read_only_files(self) -> list[str]:
        """Get list of read-only files from comma-separated string."""
        if not self.READ_ONLY_FILES or not self.READ_ONLY_FILES.strip():
            return []
        return [item.strip() for item in self.READ_ONLY_FILES.split(',') if item.strip()]
    
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

