# Dev image for the FastAPI backend (also runs the Celery worker/beat via a
# `command:` override in docker-compose).
#
# The virtualenv lives at /opt/venv (OUTSIDE /app) so the compose bind mount of
# the source over /app does NOT shadow it — that is what enables hot reload while
# keeping the installed dependencies. The production image (./Dockerfile) keeps the
# venv at /app/.venv and is used by docker-compose.prod.yml.
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_FROZEN=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 1) Install dependencies first (cached until the lockfile changes)…
COPY pyproject.toml uv.lock ./
RUN uv sync --no-install-project

# 2) …then the project itself.
COPY . .
RUN uv sync

EXPOSE 8000
# Hot-reload dev server. WATCHFILES_FORCE_POLLING (set in compose) makes the
# reloader notice changes through the Windows bind mount.
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
