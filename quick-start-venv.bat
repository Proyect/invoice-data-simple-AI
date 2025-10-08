@echo off
echo 🐍 Document Extractor API - Inicio Rápido con Entorno Virtual
echo ============================================================

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado. Por favor instala Python 3.8+ primero.
    pause
    exit /b 1
)

echo ✅ Python detectado:
python --version

REM Verificar si ya existe entorno virtual
if exist ".venv" (
    echo ✅ Entorno virtual encontrado
) else (
    echo 🔧 Configurando entorno virtual por primera vez...
    call setup_venv.bat
)

REM Activar entorno virtual
echo ⚡ Activando entorno virtual...
call .venv\Scripts\activate

REM Verificar Tesseract
echo 🔍 Verificando Tesseract...
tesseract --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Tesseract no encontrado. Instala para mejor funcionalidad:
    echo    Descarga desde https://github.com/UB-Mannheim/tesseract/wiki
) else (
    echo ✅ Tesseract encontrado
)

REM Verificar PostgreSQL (opcional)
echo 🔍 Verificando PostgreSQL...
psql --version >nul 2>&1
if errorlevel 1 (
    echo ℹ️  PostgreSQL no encontrado - usando SQLite por defecto
) else (
    echo ✅ PostgreSQL encontrado (opcional para usar SQLite)
)

REM Verificar Redis (opcional)
echo 🔍 Verificando Redis...
redis-server --version >nul 2>&1
if errorlevel 1 (
    echo ℹ️  Redis no encontrado - funcionalidad de cache limitada
) else (
    echo ✅ Redis encontrado
)

REM Iniciar aplicación
echo.
echo 🚀 Iniciando aplicación...
echo 📖 Documentación: http://localhost:8005/docs
echo 🔍 Health check: http://localhost:8005/health
echo ℹ️  Presiona Ctrl+C para detener
echo.

python main.py
