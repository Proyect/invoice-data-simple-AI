#!/usr/bin/env bash
# Backend en modo local (sin Docker): requiere .env, PostgreSQL/Redis o fallback SQLite
set -e
cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
  if [ -f env.example ]; then
    cp env.example .env
    echo "Creado .env desde env.example. Revisa DATABASE_URL y REDIS si usas Docker para DB."
  else
    echo "No existe .env ni env.example. Crea .env con al menos DATABASE_URL, SECRET_KEY."
    exit 1
  fi
fi

export PYTHONPATH="${PWD}/src"
echo "Iniciando backend (uvicorn)..."
exec python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8005
