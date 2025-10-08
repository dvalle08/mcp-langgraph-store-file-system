# Memory Configuration Files

This directory contains JSON configuration files that define memory categories and files for the MCP server.

## How It Works

- **Each JSON file = One memory category**
- **Filename (without .json) = Category name**
- **Files ending in `.example` are ignored by the system**

## Structure

```
files/
  memories.json              # Category: "memories"
  programming-style.json     # Category: "programming-style"  
  custom-category.json       # Category: "custom-category"
  *.json.example             # Examples (not loaded)
```

## JSON File Format

Each JSON file should follow this structure:

```json
{
  "files": [
    {
      "file_name": "your-file-name",
      "file_description": "What this memory stores",
      "read_trigger": "When the AI should read this",
      "write_trigger": "When the AI should create this",
      "update_trigger": "When the AI should update this"
    }
  ]
}
```

## Example

**File: `memories.json`** (creates category "memories")

```json
{
  "files": [
    {
      "file_name": "programming-style",
      "file_description": "User's programming patterns and preferences",
      "read_trigger": "When programming or working on code",
      "write_trigger": "When first tracking programming patterns",
      "update_trigger": "When errors are corrected or patterns emerge"
    },
    {
      "file_name": "communication-preferences",
      "file_description": "How user prefers responses",
      "read_trigger": "At start of conversations",
      "write_trigger": "When user expresses preferences",
      "update_trigger": "When preferences change"
    }
  ]
}
```

## Creating New Categories

1. Create a new `.json` file in this directory
2. Name it according to your category (e.g., `my-category.json`)
3. Add your file configurations inside
4. Restart the MCP server

## Pre-configured Files

- `memories.json` - Default memory files for programming, communication, and writing styles
- `memories.json.example` - Template for creating new categories

