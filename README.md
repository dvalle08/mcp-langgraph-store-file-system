# MCP LangGraph Memory Store

**A vendor-agnostic long‑term memory layer for AI agents.**

This exists for two reasons:
- The filesystem is a core capability in deep agents, so this server exposes a simple memory filesystem, inspired by [Deep Agents](https://github.com/langchain-ai/deepagents).
- Store memories in your own infrastructure so any agent (Cursor, Claude Code, ChatGPT, etc.) can share them.

### Built on LangGraph Store
Docs: [LangGraph Store](https://reference.langchain.com/python/langgraph/store/)

## Features
- **Your Choice of Backend**: Redis, PostgreSQL, or MongoDB
- **Filesystem Interface**: Read, write, and organize memories like files
- **Cross-Tool Memory**: Share the same memories across different AI agents
- **Full Control**: Your data, your infrastructure, your rules

## Quick Start

### 1. Install Dependencies

```bash
uv sync
```

### 2. Configure Environment

```bash
cp env.example .env
# Edit .env - choose your backend (redis/postgresql/mongodb)
```

### 3. Start Your Backend

**Redis:**
```bash
docker run -d -p 6379:6379 redis:latest
```

**PostgreSQL:**
```bash
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:latest
```

**MongoDB:**
```bash
docker run -d -p 27017:27017 mongo:latest
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
# Backend: Choose your storage
BACKEND=redis  # redis, postgresql, or mongodb

# Redis Configuration
REDIS_HOST=your-redis-host
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# PostgreSQL Configuration
POSTGRES_HOST=your-postgres-host
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DATABASE=langgraph_store

# MongoDB Configuration
MONGODB_URI=mongodb://your-mongodb-host:27017
MONGODB_DATABASE=langgraph_store
MONGODB_COLLECTION=memory_store

# Transport: 'stdio' for AI clients, 'streamable-http' for HTTP
TRANSPORT=stdio

# Optional: Configuration directory (default: files)
CONFIG_DIR=files
```

### Memory Configuration

Memory configurations are defined in JSON files within the `files/` directory. Each JSON file represents a memory category, and the filename (without .json) becomes the category name.

**Setup:**

1. The `files/` directory contains your memory configurations
2. Each `.json` file defines a category (e.g., `memories.json` → category "memories")
3. Inside each JSON file, define the individual files:

```json
{
  "files": [
    {
      "file_name": "programming-style",
      "file_description": "User's programming patterns and preferences",
      "read_trigger": "When programming or working on code",
      "write_trigger": "When first tracking programming patterns",
      "update_trigger": "When errors are corrected or new patterns emerge"
    }
  ]
}
```

**Structure:**

```
files/
  memories.json              # Category: "memories"
  programming-style.json     # Category: "programming-style"
  custom-category.json       # Category: "custom-category"
  *.json.example             # Example files (ignored by system)
```

**Configuration Fields:**

- `file_name`: The memory file identifier
- `file_description`: What this memory stores
- `read_trigger`: When the AI should read this memory
- `write_trigger`: When the AI should create this memory
- `update_trigger`: When the AI should update this memory

**Note:** The server must be restarted after modifying configuration files.

## AI Client Integration

### Cursor IDE

**Configuration (JSON):**
```json
{
  "mcpServers": {
    "memory-store": {
      "command": "python",
      "args": ["src/server.py"],
      "cwd": "/absolute/path/to/mcp-langgraph-store-file-system",
      "env": {
        "REDIS_HOST": "your-redis-host",
        "REDIS_PORT": "6379",
        "REDIS_PASSWORD": "",
        "REDIS_DB": "0"
      }
    }
  }
}
```

### Claude Desktop
**Configuration (JSON):**
```json
{
  "mcpServers": {
    "memory-store": {
      "command": "python",
      "args": ["src/server.py"],
      "cwd": "/absolute/path/to/mcp-langgraph-store-file-system",
      "env": {
        "REDIS_HOST": "your-redis-host",
        "REDIS_PORT": "6379",
        "REDIS_PASSWORD": "",
        "REDIS_DB": "0"
      }
    }
  }
}
```

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

### `ls(memory_category="")` - List Categories/Memories
- Empty memory_category: List all memory categories
- With memory_category: List memories in that category

### `read_file(memory_category, file_name)` - Read Memory
- Returns content and metadata for a memory

### `write_file(memory_category, file_name, content)` - Create/Update Memory
- Creates or overwrites a memory

### `edit_file(memory_category, file_name, content)` - Update Existing Memory
- Updates existing memory (fails if doesn't exist)

## Transport Modes

### stdio (Default)
For AI clients like Claude Desktop and Cursor. The server communicates via standard input/output.

### streamable-http
For HTTP access. Set `TRANSPORT=streamable-http` in `.env` and access at `http://your-host:8000`.

## Project Structure

```
src/
├── core/              # Foundational infrastructure
│   ├── settings.py    # Environment configuration
│   ├── logger.py      # Logging
│   └── file_config.py # Memory configuration
├── database/          # Data access layer
│   ├── redis_langgraph_client.py
│   ├── postgresql_langgraph_client.py
│   ├── mongodb_langgraph_client.py
│   └── store_factory.py
├── services/          # Business logic
│   └── file_store.py  # Memory operations
└── server.py          # MCP server
```

## License

Apache License 2.0
