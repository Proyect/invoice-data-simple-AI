@echo off
echo 🔄 Regresando a Desarrollo Local
echo ===============================

REM 1. Detener Docker
echo ⏹️ Deteniendo servicios Docker...
docker-compose --version >nul 2>&1
if not errorlevel 1 (
    docker-compose down
    echo ✅ Servicios Docker detenidos
) else (
    echo ⚠️  Docker Compose no encontrado
)

REM 2. Verificar entorno virtual
echo 🐍 Verificando entorno virtual...
if exist ".venv" (
    echo ✅ Entorno virtual encontrado
) else (
    echo ❌ Entorno virtual no encontrado. Ejecuta: make setup-venv
    pause
    exit /b 1
)

REM 3. Activar entorno virtual
echo ⚡ Activando entorno virtual...
call .venv\Scripts\activate

REM 4. Verificar dependencias
echo 📚 Verificando dependencias...
python -c "import fastapi, sqlalchemy" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Dependencias faltantes. Ejecutando: pip install -r requirements-venv.txt
    pip install -r requirements-venv.txt
) else (
    echo ✅ Dependencias principales OK
)

REM 5. Configurar variables de entorno para local
echo 📝 Configurando para desarrollo local...
if exist ".env" (
    REM Hacer backup del .env actual
    copy .env .env.docker.backup >nul
    echo ✅ Backup de .env guardado como .env.docker.backup
)

REM Crear .env para desarrollo local
echo # Configuración para desarrollo local > .env
echo APP_NAME=Document Extractor API - Dev >> .env
echo DEBUG=True >> .env
echo HOST=0.0.0.0 >> .env
echo PORT=8005 >> .env
echo. >> .env
echo # SQLite para desarrollo rápido >> .env
echo DATABASE_URL=sqlite:///./data/documents.db >> .env
echo. >> .env
echo # Redis local (opcional) >> .env
echo REDIS_URL=redis://localhost:6379 >> .env
echo REDIS_HOST=localhost >> .env
echo REDIS_PORT=6379 >> .env
echo REDIS_DB=0 >> .env
echo. >> .env
echo # Directorios >> .env
echo UPLOAD_DIR=uploads >> .env
echo OUTPUT_DIR=outputs >> .env
echo. >> .env
echo # Tesseract local >> .env
echo TESSERACT_CMD= >> .env
echo. >> .env
echo # Configuración OCR >> .env
echo GOOGLE_VISION_DAILY_LIMIT=200 >> .env
echo AWS_TEXTRACT_DAILY_LIMIT=100 >> .env
echo TESSERACT_CONFIDENCE_THRESHOLD=0.7 >> .env
echo. >> .env
echo # Configuración LLM (opcional) >> .env
echo OPENAI_API_KEY= >> .env
echo OPENAI_MODEL=gpt-3.5-turbo >> .env
echo OPENAI_MAX_TOKENS=1000 >> .env
echo OPENAI_TEMPERATURE=0 >> .env
echo. >> .env
echo # Configuración AWS (opcional) >> .env
echo AWS_ACCESS_KEY_ID= >> .env
echo AWS_SECRET_ACCESS_KEY= >> .env
echo AWS_REGION=us-east-1 >> .env
echo. >> .env
echo # Configuración Google Cloud (opcional) >> .env
echo GOOGLE_APPLICATION_CREDENTIALS= >> .env
echo. >> .env
echo # Procesamiento asíncrono >> .env
echo RQ_WORKER_TIMEOUT=600 >> .env
echo RQ_QUEUE_NAME=document_processing >> .env

echo ✅ Archivo .env configurado para desarrollo local

REM 6. Crear directorio de datos si no existe
echo 📁 Preparando directorios...
mkdir uploads 2>nul
mkdir outputs 2>nul
mkdir data 2>nul
mkdir logs 2>nul

echo. > uploads\.gitkeep
echo. > outputs\.gitkeep
echo. > data\.gitkeep
echo. > logs\.gitkeep

REM 7. Verificar Tesseract
echo 🔍 Verificando Tesseract...
tesseract --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Tesseract no encontrado. Instala para mejor funcionalidad:
    echo    Descarga desde https://github.com/UB-Mannheim/tesseract/wiki
) else (
    echo ✅ Tesseract encontrado
)

REM 8. Verificar PostgreSQL (opcional)
echo 🔍 Verificando PostgreSQL...
psql --version >nul 2>&1
if errorlevel 1 (
    echo ℹ️  PostgreSQL no encontrado - usando SQLite por defecto
) else (
    echo ✅ PostgreSQL encontrado (opcional para usar SQLite)
)

REM 9. Verificar Redis (opcional)
echo 🔍 Verificando Redis...
redis-server --version >nul 2>&1
if errorlevel 1 (
    echo ℹ️  Redis no encontrado - funcionalidad de cache limitada
) else (
    echo ✅ Redis encontrado
)

REM 10. Iniciar aplicación local
echo.
echo 🚀 Iniciando desarrollo local...
echo 📖 Documentación: http://localhost:8005/docs
echo 🔍 Health check: http://localhost:8005/health
echo ℹ️  Presiona Ctrl+C para detener
echo.

python main.py
