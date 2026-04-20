# Code-editing agent (Python)

Small terminal “agent loop” demos: each script isolates one concept.

- `agent_fs.py`: a single `fs` tool (list/read/write files under the working directory)
- `agent_exec.py`: a single `exec` tool (runs shell commands verbatim; Docker-only)
- `agent_exec_litellm.py`: same `exec` tool, but uses LiteLLM so you can choose model/provider

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

## Docker

```bash
docker build -t quecto-agent -f docker/Dockerfile .
```

## Exec agents (Docker only)

These agents run arbitrary shell commands. They refuse to run unless `QUECTO_DOCKER=1` (set in `docker/Dockerfile`).

```bash
# OpenAI (gpt-5.4)
docker run -it --rm -e OPENAI_API_KEY quecto-agent agent_exec.py

# LiteLLM (OpenAI)
docker run -it --rm -e OPENAI_API_KEY quecto-agent agent_exec_litellm.py --model gpt-5.4

# LiteLLM (Anthropic)
docker run -it --rm -e ANTHROPIC_API_KEY quecto-agent agent_exec_litellm.py --model anthropic/claude-opus-4-7
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
