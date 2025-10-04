"""MCP Server for LangGraph Memory Store."""

from fastmcp import FastMCP
from src.database.memory_store import memory_store
from src.core.logger import get_logger
from src.core.settings import settings

logger = get_logger("mcp_server")

mcp = FastMCP("LangGraph Memory Store")


@mcp.tool(
    name="ls",
    annotations={"readOnlyHint": True},
    description="""List available memory namespaces or memories within a namespace.

This tool allows you to explore the available memory namespaces (categories)
and the memories (files) within each namespace.

Args:
    path: Optional path to explore:
        - Empty string ("") or omit: Lists all available namespaces
        - "namespace_name": Lists all memories/files in that namespace

Returns:
    dict: Contains either:
        - "namespaces": List of available namespace objects with file counts
        - "memories": List of memory objects in the specified namespace

Examples:
    ls() -> Lists all namespaces
    ls("programming-style") -> Lists all memories in programming-style namespace
"""
)
async def ls(path: str = "") -> dict:
    """List available memories and namespaces."""
    try:
        if not path:
            # List all namespaces
            namespaces = await memory_store.list_namespaces()
            logger.info(f"Listed {len(namespaces)} namespaces")
            return {
                "type": "namespaces",
                "count": len(namespaces),
                "namespaces": namespaces
            }
        else:
            # List memories in the specified namespace
            memories = await memory_store.list_memories(path)
            logger.info(f"Listed {len(memories)} memories in namespace '{path}'")
            return {
                "type": "memories",
                "namespace": path,
                "count": len(memories),
                "memories": memories
            }
    except Exception as e:
        logger.error(f"Error in ls: {str(e)}")
        return {
            "error": str(e),
            "type": "error"
        }


@mcp.tool(
    name="read_file",
    annotations={"readOnlyHint": True},
    description="""Read a memory/file from the store.

Use this tool to retrieve the content of a specific memory. This is useful
when you need to recall user preferences, context, or any previously stored
information.

Args:
    namespace: The memory category/namespace (e.g., "programming-style", "preferences")
    key: The specific memory identifier within the namespace

Returns:
    dict: Memory data including:
        - content: The actual memory content
        - namespace: The namespace it belongs to
        - key: The memory identifier
        - is_read_only: Whether this memory is protected from modification
        - created_at: When the memory was created
        - updated_at: When the memory was last updated

Examples:
    read_file("programming-style", "python-preferences")
    read_file("writing-style", "tone")
"""

)
async def read_file(namespace: str, key: str) -> dict:
    """Read a memory/file content from the store."""
    try:
        result = await memory_store.get_memory(namespace, key)
        logger.info(f"Read memory: {namespace}/{key}")
        return result
    except FileNotFoundError as e:
        logger.warning(f"Memory not found: {namespace}/{key}")
        return {
            "error": str(e),
            "type": "not_found"
        }
    except PermissionError as e:
        logger.warning(f"Permission denied: {namespace}/{key}")
        return {
            "error": str(e),
            "type": "permission_denied"
        }
    except Exception as e:
        logger.error(f"Error reading memory: {str(e)}")
        return {
            "error": str(e),
            "type": "error"
        }


@mcp.tool(
    name="write_file",
    description="""Create or overwrite a memory/file in the store.

Use this tool to save new memories or update existing ones. This will create
the namespace if it doesn't exist and will overwrite any existing memory with
the same key.

Args:
    namespace: The memory category/namespace (e.g., "programming-style", "preferences")
    key: The memory identifier (use descriptive names like "python-type-hints")
    content: The content to store (can be any text, instructions, preferences, etc.)

Returns:
    dict: Operation result including:
        - success: Whether the operation succeeded
        - message: Success or error message
        - namespace: The namespace used
        - key: The memory identifier
        - created_at: Timestamp of creation
        - updated_at: Timestamp of last update

Examples:
    write_file("programming-style", "python-preferences", "Always use type hints and docstrings")
    write_file("preferences", "communication-style", "Be concise and direct")
"""
)
async def write_file(namespace: str, key: str, content: str) -> dict:
    """Create or overwrite a memory/file in the store."""
    try:
        result = await memory_store.put_memory(namespace, key, content)
        logger.info(f"Wrote memory: {namespace}/{key}")
        return result
    except PermissionError as e:
        logger.warning(f"Permission denied writing: {namespace}/{key}")
        return {
            "success": False,
            "error": str(e),
            "type": "permission_denied"
        }
    except ValueError as e:
        logger.warning(f"Invalid input: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "type": "validation_error"
        }
    except Exception as e:
        logger.error(f"Error writing memory: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "type": "error"
        }


@mcp.tool(
    name="edit_file",
    description="""Edit an existing memory/file.

Use this tool to update an existing memory. Unlike write_file, this will fail
if the memory doesn't exist, providing safety against typos in key names.

Args:
    namespace: The memory category/namespace
    key: The memory identifier (must exist)
    content: The new content to replace the existing content

Returns:
    dict: Operation result including:
        - success: Whether the operation succeeded
        - message: Success or error message
        - namespace: The namespace used
        - key: The memory identifier
        - created_at: Original creation timestamp
        - updated_at: New update timestamp

Examples:
    edit_file("programming-style", "python-preferences", "Updated preferences...")
    edit_file("context", "project-background", "Additional context...")
"""
)
async def edit_file(namespace: str, key: str, content: str) -> dict:
    """Edit an existing memory/file (fails if it doesn't exist)."""
    try:
        result = await memory_store.update_memory(namespace, key, content)
        logger.info(f"Updated memory: {namespace}/{key}")
        return result
    except FileNotFoundError as e:
        logger.warning(f"Memory not found for update: {namespace}/{key}")
        return {
            "success": False,
            "error": str(e),
            "type": "not_found"
        }
    except PermissionError as e:
        logger.warning(f"Permission denied updating: {namespace}/{key}")
        return {
            "success": False,
            "error": str(e),
            "type": "permission_denied"
        }
    except ValueError as e:
        logger.warning(f"Invalid input: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "type": "validation_error"
        }
    except Exception as e:
        logger.error(f"Error updating memory: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "type": "error"
        }


if __name__ == "__main__":
    transport = settings.TRANSPORT.lower()
    
    if transport == "stdio":
        logger.info("Starting MCP server with stdio transport")
        mcp.run(transport="stdio")
    elif transport == "streamable-http":
        logger.info(f"Starting MCP server with streamable-http transport on {settings.HOST}:{settings.PORT}")
        mcp.run(transport="streamable-http", host=settings.HOST, port=settings.PORT)
    else:
        raise ValueError(f"Invalid transport mode: {transport}. Must be 'stdio' or 'streamable-http'")
