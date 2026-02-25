@echo off
cd /d "%~dp0\.."
REM Backend en modo local (sin Docker): requiere .env, PostgreSQL/Redis o fallback SQLite
echo Verificando .env...
if not exist .env (
  if exist env.example (
    copy env.example .env
    echo Creado .env desde env.example. Revisa DATABASE_URL y REDIS si usas Docker para DB.
  ) else (
    echo No existe .env ni env.example. Crea .env con al menos DATABASE_URL, SECRET_KEY.
    exit /b 1
  )
)

echo Iniciando backend (uvicorn)...
set PYTHONPATH=%CD%\src
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8005
