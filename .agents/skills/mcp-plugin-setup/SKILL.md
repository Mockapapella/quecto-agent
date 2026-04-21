---
name: mcp-plugin-setup
description: Create or update mcp.json to load MCP plugins (stdio servers) for agent_full.py.
---

# mcp-plugin-setup

## Goal

Enable MCP plugins for `agent_full.py` by creating or editing `mcp.json` at the repo root.

## Steps

1. Check whether `mcp.json` exists with `exec({"cmd":"ls -la mcp.json || true"})` and `exec({"cmd":"cat mcp.json"})`.
2. If missing, create it with a heredoc via `exec`, e.g. `exec({"cmd":"cat > mcp.json <<'EOF'\\n...\\nEOF"})`.
3. Add one or more plugins under `mcpServers`.

## Example

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest", "--headless", "--browser", "chromium", "--no-sandbox"]
    },
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch"]
    }
  }
}
```

## Notes

- This agent currently supports stdio MCP plugins configured via `command` + `args`.
