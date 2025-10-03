FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS base
FROM base AS builder

RUN apt-get update && \
    apt-get install -y curl gnupg ca-certificates bash

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/venv

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --all-groups;

COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --all-groups

FROM base

RUN apt-get update && \
    apt-get install -y curl gnupg ca-certificates bash && \
    curl -fsSL https://raw.githubusercontent.com/tj/n/master/bin/n | bash -s lts && \
    node -v && npx -v

COPY --from=builder /app /app

WORKDIR /app
ENV PATH="/app/venv/bin:$PATH"

EXPOSE 8000

RUN ["uv", "run", "python", "-m", "app.main"]
