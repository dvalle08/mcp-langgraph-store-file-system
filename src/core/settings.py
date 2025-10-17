import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from core.file_config import FileConfigManager

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
    
    # User Configuration
    USER_ID: str = Field(default="default-user", description="User identifier for memory store")
    
    # Redis configuration
    redis: RedisSettings = Field(default_factory=RedisSettings)
    
    # Memory Store Configuration
    CONFIG_DIR: str = Field(
        default="files",
        description="Directory containing JSON configuration files for memories"
    )
    ALLOWED_FILES: str = Field(
        default="",
        description="Comma-separated list of allowed file names. Empty means all files are allowed."
    )
    READ_ONLY_FILES: str = Field(
        default="",
        description="Comma-separated list of read-only files in format 'memory_category/file_name'"
    )
    ENABLE_AGENT_FILES: bool = Field(
        default=False,
        description="Allow agent to create files in 'agent_files' category for plans and notes"
    )
    AGENT_FILES_CATEGORY: str = Field(
        default="agent_files",
        description="Category name for agent-created files"
    )
    file_config: FileConfigManager | None = Field(
        default=None,
        description="File configuration manager instance"
    )
    
    def get_allowed_files(self) -> list[str]:
        """Get list of allowed file names from comma-separated string."""
        if not self.ALLOWED_FILES or not self.ALLOWED_FILES.strip():
            return []
        return [item.strip() for item in self.ALLOWED_FILES.split(',') if item.strip()]
    
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
        # Initialize file config manager
        allowed_files = self.get_allowed_files()
        self.model_fields_set.add('file_config')  # Mark file_config as set
        self.file_config = FileConfigManager(
            config_dir=self.CONFIG_DIR,
            allowed_files=allowed_files if allowed_files else None
        )


# Global settings instance
settings = Settings()

