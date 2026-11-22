FROM python:3.13-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

RUN python -m pip install --no-cache-dir uv==0.12.10

COPY pyproject.toml uv.lock ./
COPY apps ./apps
COPY packages ./packages

RUN uv sync --frozen --no-dev --package aeo-worker

FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

RUN apt-get update \
    && apt-get upgrade -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* \
    && PYTHON_SITE_PACKAGES="$(python -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])')" \
    && rm -rf "$PYTHON_SITE_PACKAGES/pip" "$PYTHON_SITE_PACKAGES"/pip-*.dist-info \
        "$PYTHON_SITE_PACKAGES/setuptools" "$PYTHON_SITE_PACKAGES"/setuptools-*.dist-info \
        "$PYTHON_SITE_PACKAGES/wheel" "$PYTHON_SITE_PACKAGES"/wheel-*.dist-info \
    && rm -f /usr/local/bin/pip /usr/local/bin/pip3 /usr/local/bin/pip3.* \
    && groupadd --system --gid 10001 aeo \
    && useradd --system --uid 10001 --gid aeo --home-dir /app --no-create-home aeo

COPY --from=builder --chown=aeo:aeo /app/.venv /app/.venv
COPY --from=builder --chown=aeo:aeo /app/apps/worker /app/apps/worker
COPY --from=builder --chown=aeo:aeo /app/packages /app/packages

USER aeo

CMD ["python", "-m", "aeo_worker"]
