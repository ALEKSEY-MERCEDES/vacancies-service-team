#!/bin/sh
set -e

HOST="${DB_HOST:-db}"
PORT="${DB_PORT:-5432}"

echo "Waiting for DB at $HOST:$PORT..."

python - <<'PY'
import os, socket, time
host = os.getenv("DB_HOST", "db")
port = int(os.getenv("DB_PORT", "5432"))

while True:
    try:
        with socket.create_connection((host, port), timeout=2):
            print("DB is up!")
            break
    except OSError:
        time.sleep(1)
PY
