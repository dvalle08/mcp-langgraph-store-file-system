"""File Store Manager for LangGraph Redis Store operations."""

import re
from datetime import datetime
from typing import Optional, Any

from core.logger import get_logger
from core.settings import settings
from database.redis_langgraph_client import redis_connection

logger = get_logger("file_store")


class FileStore:
    """Wrapper class for LangGraph store operations with validation and metadata."""
    
    def __init__(self):
        self.settings = settings
        self._validate_pattern = re.compile(r'^[a-zA-Z0-9_-]+$')
    
    @property
    def USER_ID(self) -> str:
        """Get the user ID from settings."""
        return self.settings.USER_ID
    
    def _is_namespace_allowed(self, namespace: str) -> bool:
        """Check if namespace is in allowed list (empty list = all allowed)."""
        # For all categories, check allowed list (empty = all allowed)
        allowed = self.settings.get_allowed_files()
        if not allowed:
            return True
        
        # This method is for namespace/category checking, so always return True
        # since file-level filtering is done elsewhere
        return True
    
    def _is_read_only(self, namespace: str, key: str) -> bool:
        """Check if a file is marked as read-only."""
        file_path = f"{namespace}/{key}"
        read_only_files = self.settings.get_read_only_files()
        return file_path in read_only_files
    
    def _validate_identifier(self, identifier: str, name: str = "identifier") -> None:
        """Validate namespace or key format."""
        if not identifier:
            raise ValueError(f"{name} cannot be empty")
        if not self._validate_pattern.match(identifier):
            raise ValueError(
                f"{name} must contain only alphanumeric characters, hyphens, and underscores. Got: {identifier}"
            )
    
    async def list_namespaces(self) -> list[dict[str, Any]]:
        """List all available namespaces.
        
        Returns:
            List of namespace dictionaries with name and file count
        """
        logger.debug("Listing all namespaces")
        
        async with redis_connection.get_store() as store:
            # Search for all items to get namespaces
            items = await store.asearch((self.USER_ID,))
            
            # Extract unique namespaces
            namespaces_data = {}
            for item in items:
                namespace = item.namespace[0] if item.namespace else "default"
                
                # Check if namespace is allowed
                if not self._is_namespace_allowed(namespace):
                    continue
                
                if namespace not in namespaces_data:
                    namespaces_data[namespace] = {
                        "name": namespace,
                        "file_count": 0
                    }
                namespaces_data[namespace]["file_count"] += 1
            
            result = list(namespaces_data.values())
            logger.info(f"Found {len(result)} namespaces")
            return result
    
    async def list_memories(self, namespace: str) -> list[dict[str, Any]]:
        """List all memories in a namespace.
        
        Args:
            namespace: The namespace to list memories from
            
        Returns:
            List of memory metadata dictionaries
        """
        self._validate_identifier(namespace, "namespace")
        
        if not self._is_namespace_allowed(namespace):
            raise PermissionError(f"Namespace '{namespace}' is not in the allowed list")
        
        logger.debug(f"Listing memories in namespace: {namespace}")
        
        async with redis_connection.get_store() as store:
            items = await store.asearch((self.USER_ID, namespace))
            
            memories = []
            for item in items:
                memory_data = {
                    "key": item.key,
                    "namespace": namespace,
                    "is_read_only": self._is_read_only(namespace, item.key),
                    "created_at": item.created_at,
                    "updated_at": item.updated_at,
                }
                memories.append(memory_data)
            
            logger.info(f"Found {len(memories)} memories in namespace '{namespace}'")
            return memories
    
    async def get_memory(self, namespace: str, key: str) -> dict[str, Any]:
        """Read a memory content.
        
        Args:
            namespace: Memory category
            key: Memory identifier
            
        Returns:
            Memory data with content and metadata
        """
        self._validate_identifier(namespace, "namespace")
        self._validate_identifier(key, "key")
        
        if not self._is_namespace_allowed(namespace):
            raise PermissionError(f"Namespace '{namespace}' is not in the allowed list")
        
        logger.debug(f"Reading memory: {namespace}/{key}")
        
        async with redis_connection.get_store() as store:
            item = await store.aget((self.USER_ID, namespace), key)
            
            if item is None:
                raise FileNotFoundError(f"Memory '{key}' not found in namespace '{namespace}'")
            
            result = {
                "namespace": namespace,
                "key": key,
                "content": item.value.get("content", "") if isinstance(item.value, dict) else str(item.value),
                "is_read_only": self._is_read_only(namespace, key),
                "created_at": item.created_at,
                "updated_at": item.updated_at,
            }
            
            logger.info(f"Successfully read memory: {namespace}/{key}")
            return result
    
    async def put_memory(self, namespace: str, key: str, content: str) -> dict[str, Any]:
        """Create or overwrite a memory.
        
        Args:
            namespace: Memory category
            key: Memory identifier
            content: Memory content to store
            
        Returns:
            Success status and metadata
        """
        self._validate_identifier(namespace, "namespace")
        self._validate_identifier(key, "key")
        
        if not self._is_namespace_allowed(namespace):
            raise PermissionError(f"Namespace '{namespace}' is not in the allowed list")
        
        if self._is_read_only(namespace, key):
            raise PermissionError(f"Memory '{namespace}/{key}' is marked as read-only")
        
        logger.debug(f"Writing memory: {namespace}/{key}")
        
        async with redis_connection.get_store() as store:
            # Store with metadata
            value = {
                "content": content,
            }
            
            await store.aput((self.USER_ID, namespace), key, value)
            
            # Retrieve to get timestamps
            item = await store.aget((self.USER_ID, namespace), key)
            
            result = {
                "namespace": namespace,
                "key": key,
                "success": True,
                "message": "Memory created/updated successfully",
                "created_at": item.created_at if item else None,
                "updated_at": item.updated_at if item else None,
            }
            
            logger.info(f"Successfully wrote memory: {namespace}/{key}")
            return result
    
    async def update_memory(self, namespace: str, key: str, content: str) -> dict[str, Any]:
        """Edit an existing memory (fails if doesn't exist).
        
        Args:
            namespace: Memory category
            key: Memory identifier
            content: New content
            
        Returns:
            Success status and metadata
        """
        self._validate_identifier(namespace, "namespace")
        self._validate_identifier(key, "key")
        
        if not self._is_namespace_allowed(namespace):
            raise PermissionError(f"Namespace '{namespace}' is not in the allowed list")
        
        if self._is_read_only(namespace, key):
            raise PermissionError(f"Memory '{namespace}/{key}' is marked as read-only")
        
        logger.debug(f"Updating memory: {namespace}/{key}")
        
        async with redis_connection.get_store() as store:
            # Check if exists
            existing = await store.aget((self.USER_ID, namespace), key)
            if existing is None:
                raise FileNotFoundError(f"Memory '{key}' not found in namespace '{namespace}'. Use write_file to create new memories.")
            
            # Update with metadata
            value = {
                "content": content,
            }
            
            await store.aput((self.USER_ID, namespace), key, value)
            
            # Retrieve to get timestamps
            item = await store.aget((self.USER_ID, namespace), key)
            
            result = {
                "namespace": namespace,
                "key": key,
                "success": True,
                "message": "Memory updated successfully",
                "created_at": item.created_at if item else None,
                "updated_at": item.updated_at if item else None,
            }
            
            logger.info(f"Successfully updated memory: {namespace}/{key}")
            return result
    
    async def search_memories(self, namespace: str, pattern: str) -> list[dict[str, Any]]:
        """Search for memories by key pattern.
        
        Args:
            namespace: Memory category to search in
            pattern: Pattern to match against keys
            
        Returns:
            List of matching memories
        """
        self._validate_identifier(namespace, "namespace")
        
        if not self._is_namespace_allowed(namespace):
            raise PermissionError(f"Namespace '{namespace}' is not in the allowed list")
        
        logger.debug(f"Searching memories in {namespace} with pattern: {pattern}")
        
        memories = await self.list_memories(namespace)
        
        # Simple pattern matching (can be enhanced)
        matching = [m for m in memories if pattern.lower() in m["key"].lower()]
        
        logger.info(f"Found {len(matching)} matching memories")
        return matching


# Global instance
file_store = FileStore()

