"""MCP Server for LangGraph Memory Store."""

from mcp.server import FastMCP
from database.file_store import file_store
from core.logger import get_logger
from core.settings import settings

logger = get_logger("mcp_server")

# Get file configuration manager
file_config = settings.file_config

mcp = FastMCP(
    "LangGraph Memory Store",
    host=settings.HOST,
    port=settings.PORT,
)

# Log loaded file configurations
if file_config.has_configurations():
    logger.info(f"Loaded {len(file_config.files)} file configurations")
else:
    logger.info("No file configurations loaded - server will work with generic descriptions")

@mcp.tool(
    name="ls",
    annotations={"readOnlyHint": True},
    description=f"""List available memory categories and files.

Use this to explore what memories are available:
- Without memory_category: Lists all memory categories
- With memory_category: Lists all files in that category{file_config.format_files_for_tool_description()}
"""
)
async def ls(memory_category: str = "") -> dict:
    """List available files and categories."""
    try:
        if not memory_category:
            # List all categories
            categories = await file_store.list_namespaces()
            logger.info(f"Listed {len(categories)} memory categories")
            return {
                "type": "categories",
                "count": len(categories),
                "categories": categories
            }
        else:
            # List files in the specified category
            files = await file_store.list_memories(memory_category)
            logger.info(f"Listed {len(files)} files in category '{memory_category}'")
            return {
                "type": "files",
                "memory_category": memory_category,
                "count": len(files),
                "files": files
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
    description=f"""Read a memory file to retrieve stored information.

Use this to recall user preferences, context, patterns, or any previously stored information.{file_config.format_read_triggers()}
"""

)
async def read_file(memory_category: str, file_name: str) -> dict:
    """Read a file content from the store."""
    try:
        result = await file_store.get_memory(memory_category, file_name)
        logger.info(f"Read memory: {memory_category}/{file_name}")
        return result
    except FileNotFoundError as e:
        logger.warning(f"Memory not found: {memory_category}/{file_name}")
        return {
            "error": str(e),
            "type": "not_found"
        }
    except PermissionError as e:
        logger.warning(f"Permission denied: {memory_category}/{file_name}")
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
    description=f"""Create or overwrite a memory file.

Use this to save new memories or completely replace existing ones. Creates the memory_category if it doesn't exist.{file_config.format_write_triggers()}
"""
)
async def write_file(memory_category: str, file_name: str, content: str) -> dict:
    """Create or overwrite a file in the store."""
    try:
        result = await file_store.put_memory(memory_category, file_name, content)
        logger.info(f"Wrote memory: {memory_category}/{file_name}")
        return result
    except PermissionError as e:
        logger.warning(f"Permission denied writing: {memory_category}/{file_name}")
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
    description=f"""Update an existing memory file.

Use this to modify existing memories. Fails if the memory doesn't exist (use write_file to create new memories).{file_config.format_update_triggers()}
"""
)
async def edit_file(memory_category: str, file_name: str, content: str) -> dict:
    """Edit an existing file (fails if it doesn't exist)."""
    try:
        result = await file_store.update_memory(memory_category, file_name, content)
        logger.info(f"Updated memory: {memory_category}/{file_name}")
        return result
    except FileNotFoundError as e:
        logger.warning(f"Memory not found for update: {memory_category}/{file_name}")
        return {
            "success": False,
            "error": str(e),
            "type": "not_found"
        }
    except PermissionError as e:
        logger.warning(f"Permission denied updating: {memory_category}/{file_name}")
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
        mcp.run(transport="streamable-http")
    else:
        raise ValueError(f"Invalid transport mode: {transport}. Must be 'stdio' or 'streamable-http'")
