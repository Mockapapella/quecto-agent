FROM python:3.12-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates nodejs npm && rm -rf /var/lib/apt/lists/*
RUN npx -y playwright@latest install --with-deps chromium
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH" PYTHONUNBUFFERED=1

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

COPY agent_fs.py agent_exec.py agent_exec_litellm.py agent_full.py README.md AGENTS.md mcp.json ./
COPY .agents/ .agents/
ENTRYPOINT ["uv","run"]
CMD ["agent_exec.py"]
