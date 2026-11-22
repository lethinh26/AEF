FROM python:3.13-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

RUN python -m pip install --no-cache-dir uv==0.12.10

COPY pyproject.toml uv.lock ./
COPY apps ./apps
COPY packages ./packages
COPY infra/migrations ./infra/migrations

RUN uv sync --frozen --no-dev --package aeo-api

FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

RUN apt-get update \
    && apt-get upgrade -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /usr/local/lib/python3.13/site-packages/pip /usr/local/lib/python3.13/site-packages/pip-*.dist-info /usr/local/bin/pip /usr/local/bin/pip3 /usr/local/bin/pip3.13 \
    && groupadd --system --gid 10001 aeo \
    && useradd --system --uid 10001 --gid aeo --home-dir /app --no-create-home aeo

COPY --from=builder --chown=aeo:aeo /app/.venv /app/.venv
COPY --from=builder --chown=aeo:aeo /app/apps/api /app/apps/api
COPY --from=builder --chown=aeo:aeo /app/packages /app/packages
COPY --from=builder --chown=aeo:aeo /app/infra/migrations /app/infra/migrations

USER aeo

EXPOSE 8100

CMD ["uvicorn", "aeo_api.main:app", "--host", "0.0.0.0", "--port", "8100"]
