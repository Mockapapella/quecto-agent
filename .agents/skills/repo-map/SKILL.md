---
name: repo-map
description: Map the repo structure and summarize key files using only the exec tool.
---

# repo-map

## Goal

Build a quick mental model of the repository.

## How

1. Use `exec({"cmd":"ls"})` to list the current directory.
2. Read `README.md` and the top-level `*.py` files with `exec({"cmd":"sed -n '1,200p' README.md"})` (and similar).
3. Produce a short summary:
   - what the repo does
   - what each script is for
   - what to run first

## Notes

- Use only the `exec` tool.
