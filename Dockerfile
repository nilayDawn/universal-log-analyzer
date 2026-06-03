FROM python:3.12-slim

RUN apt-get update && apt-get install -y curl build-essential bash && \
    curl -1sLf https://sh.vector.dev | bash -s -- -y && \
    apt-get clean

ENV PATH="/root/.vector/bin:${PATH}"

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN pip install --no-cache-dir uv

RUN uv sync --frozen --no-install-project

COPY . .

RUN uv sync --frozen

ENV PYTHONPATH=/app

CMD ["uv", "run", "python", "-m", "src.main"]