# syntax=docker/dockerfile:1
FROM python:3.9-slim

# Stable builds for your pinned deps (aiohttp, asyncpg, pycares, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc \
    libffi-dev libssl-dev libpq-dev \
 && rm -rf /var/lib/apt/lists/*

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install deps first for better layer caching
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Then copy your source
COPY . .

# Unbuffered logs for easier debugging
CMD ["python", "-u", "bot.py"]
