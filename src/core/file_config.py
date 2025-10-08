"""File configuration management for MCP server."""

import json
import os
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, field_validator
from core.logger import get_logger

logger = get_logger("file_config")


class FileConfig(BaseModel):
    """Configuration for a single file within a memory category."""
    
    file_name: str = Field(..., description="Memory file name (maps to LangGraph key)")
    file_description: str = Field(..., description="Description of what this memory stores")
    read_trigger: str = Field(..., description="When the agent should read this memory")
    write_trigger: str = Field(..., description="When the agent should write/create this memory")
    update_trigger: str = Field(..., description="When the agent should update this memory")
    
    @field_validator('file_name')
    @classmethod
    def validate_file_name(cls, v: str) -> str:
        """Validate file_name format."""
        if not v:
            raise ValueError("file_name cannot be empty")
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError(
                f"file_name must contain only alphanumeric characters, hyphens, and underscores. Got: {v}"
            )
        return v


class MemoryConfig(BaseModel):
    """Configuration for a single memory file with category."""
    
    memory_category: str = Field(..., description="Memory category (maps to LangGraph namespace)")
    file_name: str = Field(..., description="Memory file name (maps to LangGraph key)")
    file_description: str = Field(..., description="Description of what this memory stores")
    read_trigger: str = Field(..., description="When the agent should read this memory")
    write_trigger: str = Field(..., description="When the agent should write/create this memory")
    update_trigger: str = Field(..., description="When the agent should update this memory")
    
    @field_validator('memory_category', 'file_name')
    @classmethod
    def validate_identifier(cls, v: str) -> str:
        """Validate memory_category and file_name format."""
        if not v:
            raise ValueError("Identifier cannot be empty")
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError(
                f"Identifier must contain only alphanumeric characters, hyphens, and underscores. Got: {v}"
            )
        return v
    
    @property
    def namespace(self) -> str:
        """Get LangGraph namespace (maps from memory_category)."""
        return self.memory_category
    
    @property
    def key(self) -> str:
        """Get LangGraph key (maps from file_name)."""
        return self.file_name
    
    @property
    def full_path(self) -> str:
        """Get the full path in format memory_category/file_name."""
        return f"{self.memory_category}/{self.file_name}"


class FileConfigCollection(BaseModel):
    """Collection of file configurations within a category."""
    
    files: list[FileConfig] = Field(default_factory=list)


class FileConfigManager:
    """Manager for loading and accessing file configurations from files/ directory."""
    
    def __init__(self, config_dir: Optional[str] = None, allowed_files: Optional[list[str]] = None):
        """Initialize the file config manager.
        
        Args:
            config_dir: Path to the directory containing JSON configuration files. Defaults to 'files/'.
            allowed_files: List of allowed file names. If None or empty, all files are allowed.
        """
        self.config_dir = config_dir or "files"
        self.allowed_files = allowed_files or []
        self.files: list[MemoryConfig] = []
        self._files_by_path: dict[str, MemoryConfig] = {}
        self._files_by_namespace: dict[str, list[MemoryConfig]] = {}
        
        self.load_configs_from_directory()
    
    def load_configs_from_directory(self) -> None:
        """Load file configurations from all JSON files in the config directory."""
        config_dir_path = Path(self.config_dir)
        
        if not config_dir_path.exists():
            logger.warning(f"Config directory not found: {self.config_dir}")
            logger.info("Server will run without predefined file configurations")
            return
        
        if not config_dir_path.is_dir():
            logger.error(f"Config path is not a directory: {self.config_dir}")
            logger.info("Server will run without predefined file configurations")
            return
        
        all_memories: list[MemoryConfig] = []
        
        # Find all .json files in the directory
        json_files = list(config_dir_path.glob("*.json"))
        
        # Filter out .example files
        json_files = [f for f in json_files if not f.stem.endswith('.example')]
        
        if not json_files:
            logger.info(f"No JSON configuration files found in {self.config_dir}")
            return
        
        for json_file in json_files:
            # The filename (without .json) becomes the memory_category
            memory_category = json_file.stem
            
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Parse the file collection
                file_collection = FileConfigCollection(**data)
                
                # Create MemoryConfig objects with the category from filename
                for file_config in file_collection.files:
                    memory_config = MemoryConfig(
                        memory_category=memory_category,
                        file_name=file_config.file_name,
                        file_description=file_config.file_description,
                        read_trigger=file_config.read_trigger,
                        write_trigger=file_config.write_trigger,
                        update_trigger=file_config.update_trigger
                    )
                    all_memories.append(memory_config)
                
                logger.debug(f"Loaded {len(file_collection.files)} file(s) from {json_file.name}")
            
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in {json_file.name}: {e}")
                continue
            except Exception as e:
                logger.error(f"Error loading {json_file.name}: {e}")
                continue
        
        # Filter files based on allowed files
        if self.allowed_files:
            self.files = [
                mem for mem in all_memories 
                if mem.file_name in self.allowed_files
            ]
            filtered_count = len(all_memories) - len(self.files)
            if filtered_count > 0:
                logger.info(f"Filtered out {filtered_count} files not in allowed files")
        else:
            self.files = all_memories
        
        # Build lookup dictionaries
        self._files_by_path = {
            mem.full_path: mem for mem in self.files
        }
        
        self._files_by_namespace = {}
        for mem in self.files:
            if mem.memory_category not in self._files_by_namespace:
                self._files_by_namespace[mem.memory_category] = []
            self._files_by_namespace[mem.memory_category].append(mem)
        
        logger.info(f"Loaded {len(self.files)} file configurations from {self.config_dir}")
        
        # Log configured files
        for mem in self.files:
            logger.debug(f"  - {mem.memory_category}/{mem.file_name}: {mem.file_description}")
    
    def get_file_config(self, memory_category: str, file_name: str) -> Optional[MemoryConfig]:
        """Get file configuration by memory_category and file_name.
        
        Args:
            memory_category: Memory category
            file_name: File name
            
        Returns:
            MemoryConfig if found, None otherwise
        """
        full_path = f"{memory_category}/{file_name}"
        return self._files_by_path.get(full_path)
    
    def get_files_by_category(self, memory_category: str) -> list[MemoryConfig]:
        """Get all file configurations for a category.
        
        Args:
            memory_category: Memory category
            
        Returns:
            List of MemoryConfig objects
        """
        return self._files_by_namespace.get(memory_category, [])
    
    def get_all_categories(self) -> list[str]:
        """Get list of all configured categories.
        
        Returns:
            List of category names
        """
        return list(self._files_by_namespace.keys())
    
    def has_configurations(self) -> bool:
        """Check if any file configurations are loaded.
        
        Returns:
            True if configurations exist, False otherwise
        """
        return len(self.files) > 0
    
    def format_files_for_tool_description(self) -> str:
        """Format file configurations for tool descriptions.
        
        Returns:
            Formatted string describing configured memories
        """
        if not self.has_configurations():
            return ""
        
        lines = ["\n\nConfigured Files:"]
        
        for category in sorted(self._files_by_namespace.keys()):
            files = self._files_by_namespace[category]
            lines.append(f"\n{category}:")
            for mem in files:
                lines.append(f"  - {mem.file_name}: {mem.file_description}")
        
        return "\n".join(lines)
    
    def format_read_triggers(self) -> str:
        """Format read triggers for read_file tool description.
        
        Returns:
            Formatted string with read triggers
        """
        if not self.has_configurations():
            return ""
        
        lines = ["\n\nWhen to read:"]
        
        for mem in self.files:
            lines.append(f"  - {mem.memory_category}/{mem.file_name}: {mem.read_trigger}")
        
        return "\n".join(lines)
    
    def format_write_triggers(self) -> str:
        """Format write triggers for write_file tool description.
        
        Returns:
            Formatted string with write triggers
        """
        if not self.has_configurations():
            return ""
        
        lines = ["\n\nWhen to create:"]
        
        for mem in self.files:
            lines.append(f"  - {mem.memory_category}/{mem.file_name}: {mem.write_trigger}")
        
        return "\n".join(lines)
    
    def format_update_triggers(self) -> str:
        """Format update triggers for edit_file tool description.
        
        Returns:
            Formatted string with update triggers
        """
        if not self.has_configurations():
            return ""
        
        lines = ["\n\nWhen to update:"]
        
        for mem in self.files:
            lines.append(f"  - {mem.memory_category}/{mem.file_name}: {mem.update_trigger}")
        
        return "\n".join(lines)

