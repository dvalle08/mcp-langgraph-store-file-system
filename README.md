# MCP LangGraph Memory Store

A Model Context Protocol (MCP) server that provides persistent memory storage for AI agents using LangGraph's Redis store. Enable your AI assistants to remember preferences, context, and instructions across sessions.

## Features

- **Persistent Memory**: Store and retrieve memories across chat sessions
- **Namespace Organization**: Organize memories by category (programming-style, writing-style, preferences, etc.)
- **Read-Only Protection**: Mark memories as immutable
- **Flexible Transport**: Support for stdio and streamable-http transports
- **User-Controlled Access**: Configure accessible namespaces

## Quick Start

### 1. Install Dependencies

```bash
uv sync
```

### 2. Configure Environment

```bash
cp env.example .env
# Edit .env with your Redis credentials
```

### 3. Start Redis

```bash
# Using Docker
docker run -d -p 6379:6379 redis:latest
```

### 4. Run the Server

**For AI Clients (stdio):**
```bash
python src/server.py
```

**For HTTP Access:**
```bash
# Set TRANSPORT=streamable-http in .env
python src/server.py
```

## Configuration

Edit `.env`:

```env
# Transport: 'stdio' for AI clients, 'streamable-http' for HTTP
TRANSPORT=stdio
HOST=0.0.0.0
PORT=8000

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# Optional: Restrict namespaces (comma-separated, empty = all allowed)
ALLOWED_NAMESPACES=

# Optional: Read-only files (format: namespace/key)
READ_ONLY_FILES=
```

## AI Client Integration

### Cursor IDE

**Config Location:**
- macOS: `~/Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`
- Linux: `~/.config/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`
- Windows: `%APPDATA%\Cursor\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json`

**Configuration:**
```json
{
  "mcpServers": {
    "memory-store": {
      "command": "python",
      "args": ["src/server.py"],
      "cwd": "/absolute/path/to/mcp-langgraph-store-file-system",
      "env": {
        "REDIS_HOST": "localhost",
        "REDIS_PORT": "6379",
        "REDIS_PASSWORD": "",
        "REDIS_DB": "0"
      }
    }
  }
}
```

### Claude Desktop

**Config Location:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

Use the same JSON configuration as Cursor.

### Using uv

```json
{
  "mcpServers": {
    "memory-store": {
      "command": "uv",
      "args": ["run", "python", "src/server.py"],
      "cwd": "/absolute/path/to/mcp-langgraph-store-file-system"
    }
  }
}
```

## Available Tools

### `ls(path="")` - List Namespaces/Memories
- Empty path: List all namespaces
- With namespace: List memories in that namespace

### `read_file(namespace, key)` - Read Memory
- Returns content and metadata for a memory

### `write_file(namespace, key, content)` - Create/Update Memory
- Creates or overwrites a memory

### `edit_file(namespace, key, content)` - Update Existing Memory
- Updates existing memory (fails if doesn't exist)

## Usage Examples

### Instructing Your AI

**First Time:**
```
Check what memories I have using the ls() tool.
```

**Save Preferences:**
```
Remember my Python preferences:
- Use type hints
- Write docstrings
- Follow PEP 8
Save this in programming-style namespace as "python-preferences"
```

**Use Memories:**
```
Write a Python function following my programming preferences.
```
The AI will automatically read and apply your preferences.

## Suggested Namespaces

- `programming-style` - Coding preferences and patterns
- `writing-style` - Writing tone and structure
- `preferences` - General user preferences
- `context` - Project-specific information
- `constraints` - Requirements and limitations
- `examples` - Reference templates

## Transport Modes

### stdio (Default)
For AI clients like Claude Desktop and Cursor. The server communicates via standard input/output.

### streamable-http
For HTTP access. Set `TRANSPORT=streamable-http` in `.env` and access at `http://localhost:8000`.

## Troubleshooting

**Redis Connection Error:**
```bash
# Verify Redis is running
redis-cli ping  # Should return "PONG"
```

**Module Not Found:**
```bash
uv sync
```

**MCP Not Connecting:**
- Verify config file path is correct
- Check `cwd` points to project directory
- Restart AI client completely

## Project Structure

```
src/
├── core/
│   ├── logger.py          # Logging
│   └── settings.py        # Configuration
├── database/
│   ├── redis_langgraph_client.py  # Redis connection
│   └── memory_store.py    # Memory operations
└── server.py              # MCP server
```

## License

Apache License 2.0
