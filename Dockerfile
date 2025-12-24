FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src


# Минимальные системные зависимости (libpq-dev + gcc нужны для asyncpg/psycopg-сборок)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Установим зависимости
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Копируем код
COPY . /app

# На всякий — права на скрипт
RUN chmod +x /app/scripts/wait_for_db.sh

# дефолтную команду можно не задавать — она у тебя в docker-compose
