from fastmcp import FastMCP
from services.file_store import file_store
from core.logger import get_logger
from core.settings import settings

logger = get_logger("mcp_server")

file_config = settings.file_config

mcp = FastMCP("LangGraph Memory Store")

# Log loaded file configurations
if file_config.has_configurations():
    logger.info(f"Loaded {len(file_config.files)} file configurations")
else:
    logger.info("No file configurations loaded - server will work with generic descriptions")

@mcp.tool(
    name="ls",
    annotations={"readOnlyHint": True},
    description=f"""List configured memory files and categories.

Use this to explore what memories are available:
- Without memory_category: Lists all configured files across all categories
- With memory_category: Lists configured files in that specific category
- With show_all_available=True: Lists all namespaces in the store (shows what's accessible vs what exists){file_config.format_files_for_tool_description()}
"""
)
async def ls(memory_category: str = "", show_all_available: bool = False) -> dict:
    """List available files and categories from configuration."""
    try:
        # If show_all_available is True, list all namespaces from the store
        if show_all_available:
            all_namespaces = await file_store.list_namespaces()
            
            # Get allowed files to determine access
            allowed_files = settings.get_allowed_files()
            configured_categories = file_config.get_all_categories()
            
            # Annotate each namespace with access information
            annotated_namespaces = []
            for ns in all_namespaces:
                ns_name = ns["name"]
                # Check if this namespace has any accessible files
                has_access = False
                if not allowed_files:
                    # No restrictions, all accessible
                    has_access = True
                elif ns_name in configured_categories:
                    # Check if any files in this category are accessible
                    category_files = file_config.get_files_by_category(ns_name)
                    has_access = any(f.file_name in allowed_files for f in category_files)
                
                annotated_namespaces.append({
                    **ns,
                    "accessible": has_access,
                    "configured": ns_name in configured_categories
                })
            
            logger.info(f"Listed {len(all_namespaces)} available namespaces from store")
            return {
                "type": "all_namespaces",
                "count": len(annotated_namespaces),
                "namespaces": annotated_namespaces,
                "note": "Only files in 'accessible' and 'configured' namespaces can be read/written by the agent"
            }
        
        # List configured files from file_config
        if not memory_category:
            # List all configured files across all categories
            if not file_config.has_configurations():
                logger.info("No file configurations loaded")
                return {
                    "type": "configured_files",
                    "count": 0,
                    "files": [],
                    "note": "No file configurations loaded. Use show_all_available=True to see all namespaces in the store."
                }
            
            # Group files by category
            categories_data = {}
            for mem_config in file_config.files:
                if mem_config.memory_category not in categories_data:
                    categories_data[mem_config.memory_category] = []
                categories_data[mem_config.memory_category].append({
                    "file_name": mem_config.file_name,
                    "description": mem_config.file_description,
                    "read_trigger": mem_config.read_trigger
                })
            
            logger.info(f"Listed {len(file_config.files)} configured files across {len(categories_data)} categories")
            return {
                "type": "configured_files",
                "count": len(file_config.files),
                "categories_count": len(categories_data),
                "files_by_category": categories_data
            }
        else:
            # List files in the specified category from configuration
            category_files = file_config.get_files_by_category(memory_category)
            
            if not category_files:
                logger.info(f"No configured files in category '{memory_category}'")
                return {
                    "type": "category_files",
                    "memory_category": memory_category,
                    "count": 0,
                    "files": [],
                    "note": f"No configured files in category '{memory_category}'. Use show_all_available=True to see if this namespace exists in the store."
                }
            
            files_data = [
                {
                    "file_name": mem.file_name,
                    "description": mem.file_description,
                    "read_trigger": mem.read_trigger,
                    "write_trigger": mem.write_trigger,
                    "update_trigger": mem.update_trigger
                }
                for mem in category_files
            ]
            
            logger.info(f"Listed {len(files_data)} configured files in category '{memory_category}'")
            return {
                "type": "category_files",
                "memory_category": memory_category,
                "count": len(files_data),
                "files": files_data
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
        mcp.run(transport="streamable-http", host=settings.HOST, port=settings.PORT)
    else:
        raise ValueError(f"Invalid transport mode: {transport}. Must be 'stdio' or 'streamable-http'")
