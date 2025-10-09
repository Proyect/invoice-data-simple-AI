@echo off
echo ========================================
echo Inicializacion de Base de Datos
echo ========================================
echo.

REM Activar entorno virtual
call .venv\Scripts\activate

echo [1/3] Verificando PostgreSQL...
docker ps | findstr postgres >nul
if errorlevel 1 (
    echo PostgreSQL no esta corriendo. Iniciando...
    docker-compose up -d postgres
    timeout /t 5 /nobreak >nul
)

echo [2/3] Aplicando migraciones...
alembic upgrade head

echo [3/3] Verificando tablas creadas...
docker exec invoice-data-simple-ai-postgres-1 psql -U postgres -d document_extractor -c "\dt"

echo.
echo ========================================
echo Migracion completada exitosamente!
echo ========================================
echo.
echo Puedes iniciar la aplicacion con: python start.py
pause

