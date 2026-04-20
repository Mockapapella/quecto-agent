# Code-editing agent (Python)

Minimal terminal agent based on the Amp note “How to Build an Agent”, implemented in Python (continuous conversation).

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

## Exec Agent

```bash
uv run agent_exec.py
```

## Docker

```bash
docker build -t quecto-agent -f docker/Dockerfile .
docker run -it --rm -e OPENAI_API_KEY quecto-agent
```

## Tools exposed to the model

- `fs`: list/read/write (relative to CWD)
  - `fs({})` lists the current directory
  - `fs({"path":"file.txt"})` reads a file (or lists a directory)
  - `fs({"path":"file.txt","new_str":"..."})` overwrites/creates a file

- `exec` (in `agent_exec.py`): run a shell command (verbatim)
  - `exec({"cmd":"ls"})`
