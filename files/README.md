# Memory Configuration Files

Define memory categories and guide AI agents on when to use them.

## How It Works

- Each `.json` file = one memory category
- Filename (without `.json`) = category name
- Files ending in `.example` are ignored

## Structure

```
files/
  memories.json           # Category: "memories"
  programming.json        # Category: "programming"  
  *.json.example          # Examples (ignored)
```

## Format

```json
{
  "files": [
    {
      "file_name": "code-style",
      "file_description": "Coding preferences and patterns",
      "read_trigger": "Before generating or editing code",
      "write_trigger": "When user first expresses coding preferences",
      "update_trigger": "When preferences change or errors are corrected"
    }
  ]
}
```

## Fields

- `file_name` - Memory identifier
- `file_description` - What this memory stores
- `read_trigger` - When AI should read it
- `write_trigger` - When AI should create it
- `update_trigger` - When AI should update it

## Creating Categories

1. Create `my-category.json` in this directory
2. Add file configurations (see format above)
3. Restart the MCP server

**Triggers guide the AI** - they tell agents when to use each memory, making the system more effective.

