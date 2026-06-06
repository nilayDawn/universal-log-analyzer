FROM python:3.12-slim

# 1. Optimize environment configurations
ENV UV_COMPILE_BYTECODE=1
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV PYTHONPATH=/app

# 2. Install lightweight system utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 3. FAST INJECTION: Grab the pre-compiled uv binary directly
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 4. Copy dependency architecture files
COPY pyproject.toml uv.lock ./

# 5. CACHE LAYER: Install external libraries only (ignores dev dependencies)
RUN uv sync --frozen --no-install-project --no-dev

# 6. Copy application source code
COPY . .

# 7. FINAL LAYER: Complete project tracking and registration
RUN uv sync --frozen --no-dev

CMD ["python", "src/main.py"]