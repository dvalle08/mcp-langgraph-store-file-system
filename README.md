# MCP LangGraph Memory Store

An MCP (Model Context Protocol) server that exposes LangGraph's Redis store as a persistent memory system for AI agents. This allows you to maintain consistent memories, preferences, and context across different AI chat platforms (Claude, ChatGPT, etc.).

## Features

- **Persistent Memory Storage**: Store and retrieve memories that persist across chat sessions
- **Namespace Organization**: Organize memories into categories (programming-style, writing-style, preferences, etc.)
- **Read-Only Protection**: Mark certain memories as read-only to prevent accidental modifications
- **User-Controlled Access**: Configure which namespaces are accessible to agents
- **Metadata Tracking**: Automatic timestamps for creation and updates

## Architecture

### Memory Structure

- **Namespace**: Memory category (e.g., "programming-style", "writing-style", "preferences")
- **Key**: Memory/file name within namespace (e.g., "python-preferences", "tone")
- **Content**: The actual memory content (text, instructions, preferences, etc.)
- **Metadata**: Automatic tracking of creation time, update time, and read-only status

### Storage Backend

Uses LangGraph's Redis store for persistent, scalable storage with support for:
- Namespaced key-value storage
- Automatic timestamp tracking
- Efficient search and retrieval

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd mcp-langgraph-store-file-system
   ```

2. **Install dependencies** (using uv)
   ```bash
   uv sync
   ```

3. **Configure environment**
   ```bash
   cp env.example .env
   # Edit .env with your Redis configuration
   ```

4. **Setup Redis** (if not already running)
   ```bash
   # Using Docker
   docker run -d -p 6379:6379 redis:latest
   
   # Or install locally following Redis documentation
   ```

## Configuration

Edit your `.env` file:

```env
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password_here
REDIS_DB=0

# Memory Store Configuration
# Allowed namespaces (empty = all allowed)
ALLOWED_NAMESPACES=programming-style,writing-style,preferences,context

# Read-only files (format: namespace/key)
READ_ONLY_FILES=preferences/core-values,programming-style/company-standards
```

### Configuration Options

- **ALLOWED_NAMESPACES**: Comma-separated list of namespaces the agent can access. Leave empty to allow all namespaces.
- **READ_ONLY_FILES**: Comma-separated list of files that cannot be modified, in format `namespace/key`.

## Available Tools

The MCP server provides 4 tools for memory management:

### 1. `ls` - List Namespaces and Memories

List available namespaces or memories within a namespace.

```python
# List all namespaces
ls()
# Returns: {"namespaces": [{"name": "programming-style", "file_count": 3}, ...]}

# List memories in a namespace
ls("programming-style")
# Returns: {"memories": [{"key": "python-preferences", "is_read_only": false, ...}, ...]}
```

### 2. `read_file` - Read Memory Content

Read the content of a specific memory.

```python
read_file("programming-style", "python-preferences")
# Returns: {
#   "content": "Always use type hints and docstrings...",
#   "namespace": "programming-style",
#   "key": "python-preferences",
#   "is_read_only": false,
#   "created_at": "2024-01-01T10:00:00",
#   "updated_at": "2024-01-01T10:00:00"
# }
```

### 3. `write_file` - Create or Overwrite Memory

Create a new memory or overwrite an existing one.

```python
write_file(
    "programming-style",
    "python-preferences",
    "Always use type hints, docstrings, and follow PEP 8"
)
# Returns: {"success": true, "message": "Memory created/updated successfully", ...}
```

### 4. `edit_file` - Update Existing Memory

Update an existing memory (fails if memory doesn't exist).

```python
edit_file(
    "programming-style",
    "python-preferences",
    "Updated: Always use type hints, comprehensive docstrings, and follow PEP 8"
)
# Returns: {"success": true, "message": "Memory updated successfully", ...}
```

## Usage Examples

### Example 1: Setting Programming Preferences

**User to AI:** "Remember that I prefer Python code with type hints and detailed docstrings"

**AI uses tools:**
```python
write_file(
    namespace="programming-style",
    key="python-preferences",
    content="Always use type hints for function parameters and return values. Include detailed docstrings with parameter descriptions and examples."
)
```

### Example 2: Setting Writing Style

**User to AI:** "I prefer a professional but conversational tone in my writing"

**AI uses tools:**
```python
write_file(
    namespace="writing-style",
    key="tone",
    content="Use professional language with a conversational tone. Avoid overly formal language. Be clear and direct."
)
```

### Example 3: Recalling Preferences

**User to AI:** "Write a Python function following my preferences"

**AI uses tools:**
```python
# First, check what preferences exist
ls("programming-style")

# Then read the specific preference
read_file("programming-style", "python-preferences")

# AI then writes code following those preferences
```

### Example 4: Managing Project Context

**User to AI:** "Remember that this project is a web scraper for e-commerce sites"

**AI uses tools:**
```python
write_file(
    namespace="context",
    key="project-overview",
    content="Web scraper for e-commerce sites. Focus on product data extraction, price monitoring, and inventory tracking. Must handle rate limiting and respect robots.txt."
)
```

## Suggested Memory Namespaces

Here are recommended namespaces for organizing your memories:

- **programming-style**: Coding preferences, patterns, conventions
  - Examples: `python-preferences`, `javascript-standards`, `testing-approach`

- **writing-style**: Writing tone, vocabulary, structure preferences
  - Examples: `tone`, `vocabulary`, `document-structure`

- **preferences**: General user preferences
  - Examples: `communication-style`, `explanation-depth`, `core-values`

- **context**: Project-specific context and background
  - Examples: `project-overview`, `tech-stack`, `team-structure`

- **constraints**: Limitations or requirements to follow
  - Examples: `security-requirements`, `performance-targets`, `compatibility`

- **examples**: Reference examples for various tasks
  - Examples: `code-template`, `report-format`, `email-template`

## Running the Server

```bash
# Activate environment (if using uv)
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows

# Run the MCP server
python -m src.server
```

## Integration with AI Chats

### Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "memory-store": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/mcp-langgraph-store-file-system"
    }
  }
}
```

### ChatGPT

Follow OpenAI's MCP integration documentation to connect this server.

## Development

### Project Structure

```
mcp-langgraph-store-file-system/
├── src/
│   ├── core/
│   │   ├── logger.py          # Logging configuration
│   │   └── settings.py         # Application settings
│   ├── database/
│   │   ├── redis_langgraph_client.py  # Redis connection
│   │   └── memory_store.py     # Memory store manager
│   └── server.py               # MCP server with tools
├── env.example                 # Example environment configuration
├── pyproject.toml             # Project dependencies
└── README.md                  # This file
```

### Adding New Features

1. **Custom Validation**: Modify `memory_store.py` to add custom validation rules
2. **Additional Tools**: Add new tools in `server.py` following the existing pattern
3. **Storage Backends**: Extend to support other LangGraph stores (Postgres, MongoDB)

## Troubleshooting

### Connection Issues

If you get Redis connection errors:
1. Verify Redis is running: `redis-cli ping`
2. Check your `.env` configuration
3. Verify firewall settings

### Permission Errors

If you get permission errors:
1. Check `ALLOWED_NAMESPACES` in `.env`
2. Verify the namespace/key is not in `READ_ONLY_FILES`
3. Check namespace and key naming (only alphanumeric, hyphens, underscores)

### Memory Not Found

If memories aren't found:
1. Use `ls()` to see available namespaces
2. Use `ls("namespace")` to see available keys
3. Verify you're using the correct namespace and key

## License

Apache License 2.0 - See LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
