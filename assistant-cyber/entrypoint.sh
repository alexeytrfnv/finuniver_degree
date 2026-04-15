#!/bin/bash

set -e

echo "Запускается приложение..."
alembic upgrade head
# exec python -m app.run_broker & uvicorn app.main:app --host 0.0.0.0 --port 8000
# exec faststream run app.main:stream_app --host 0.0.0.0 --port 8000

exec uvicorn app.main:app --host 0.0.0.0 --port 8080