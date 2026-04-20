# Code-editing agent (Python)

Minimal terminal agent based on the Amp note “How to Build an Agent”, implemented in Python (continuous conversation).

## Setup

```bash
uv sync
export OPENAI_API_KEY="..."
```

## Run

```bash
uv run agent.py
```

Model: `gpt-5.4`

## Tools exposed to the model

- `fs`: list/read/write (relative to CWD)
  - `fs({})` lists the current directory
  - `fs({"path":"file.txt"})` reads a file (or lists a directory)
  - `fs({"path":"file.txt","new_str":"..."})` overwrites/creates a file
