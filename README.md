# Terminal agent (Python)

![Screenshot](assets/image.png)

Small terminal “agent loop” demos: each script isolates one concept.

- `agent_fs.py`: a single `fs` tool (list/read/write files under the working directory)
- `agent_exec.py`: a single `exec` tool (runs shell commands verbatim; Docker recommended)
- `agent_exec_litellm.py`: same `exec` tool, but uses LiteLLM so you can choose model/provider
- `agent_full.py`: `exec` (LiteLLM, Docker recommended) + AGENTS.md autoload + Skill discovery + MCP client loading

## Setup

```bash
uv sync
export OPENAI_API_KEY="..."
```

## Run

```bash
uv run agent_fs.py
```

Model: `gpt-5.4`

## agent_full.py

`agent_full.py` is the LiteLLM `exec` agent plus three “industry standard” integrations:

- **AGENTS.md**: loads `./AGENTS.md` and includes it in the system prompt.
- **Skills**: loads repo-local skills from `./.agents/skills/*/SKILL.md` into the system prompt.
- **MCP**: loads MCP plugins from `mcp.json` and exposes MCP tools as function tools.

This repo includes example skills under `./.agents/skills/`.

Run:

```bash
docker run -it --rm -e OPENAI_API_KEY quecto-agent agent_full.py --model gpt-5.4
```

### MCP config

`agent_full.py` always reads MCP plugins from `./mcp.json` (repo root). This repo includes example plugins in `mcp.json`.

Example:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest", "--headless", "--browser", "chromium", "--no-sandbox"]
    },
    "fetch": {
      "command": "uvx",
      "args": ["--with", "readabilipy==0.2.0", "mcp-server-fetch"]
    }
  }
}
```

Note: `docker/Dockerfile` installs `nodejs`/`npm` (`npx`), `uv` (`uvx`), and Playwright Chromium (for `@playwright/mcp`).

## Docker

```bash
docker build -t quecto-agent -f docker/Dockerfile .
```

## Exec agents (Docker recommended)

These agents run arbitrary shell commands. Run them in Docker.

```bash
# OpenAI (gpt-5.4)
docker run -it --rm -e OPENAI_API_KEY quecto-agent agent_exec.py

# LiteLLM (OpenAI)
docker run -it --rm -e OPENAI_API_KEY quecto-agent agent_exec_litellm.py --model gpt-5.4

# LiteLLM (Anthropic)
docker run -it --rm -e ANTHROPIC_API_KEY quecto-agent agent_exec_litellm.py --model anthropic/claude-opus-4-7

# LiteLLM + extras (AGENTS.md + skills + MCP)
docker run -it --rm -e OPENAI_API_KEY quecto-agent agent_full.py --model gpt-5.4
```

## Tools exposed to the model

- `fs`: list/read/write (relative to CWD)
  - `fs({})` lists the current directory
  - `fs({"path":"file.txt"})` reads a file (or lists a directory)
  - `fs({"path":"file.txt","new_str":"..."})` overwrites/creates a file

- `exec` (in `agent_exec.py`): run a shell command (verbatim)
  - `exec({"cmd":"ls"})`

- `exec` (in `agent_exec_litellm.py`): same tool, but model/provider selected via LiteLLM
  - `docker run -it --rm -e ANTHROPIC_API_KEY quecto-agent agent_exec_litellm.py --model anthropic/claude-opus-4-7`

- `agent_full.py`: `exec` plus any MCP tools loaded from `mcp.json`
