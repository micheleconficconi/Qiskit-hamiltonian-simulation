FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 MPLBACKEND=Agg

WORKDIR /app

# 1) dependencies first: cached unless the lock file changes
COPY requirements-dev.txt ./
RUN pip install -r requirements-dev.txt

# 2) project code
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-deps -e .
COPY tests ./tests
COPY experiments ./experiments

CMD ["pytest", "-q", "-m", "not slow"]
