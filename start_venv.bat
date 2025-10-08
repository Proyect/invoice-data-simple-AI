@echo off
echo 🚀 Iniciando Document Extractor API con Entorno Virtual
echo ======================================================

REM Verificar si existe el entorno virtual
if not exist ".venv" (
    echo ❌ Entorno virtual no encontrado. Ejecuta primero: setup_venv.bat
    pause
    exit /b 1
)

REM Activar entorno virtual
echo ⚡ Activando entorno virtual...
call .venv\Scripts\activate

REM Verificar instalación
echo 🔍 Verificando instalación...
python -c "import fastapi, sqlalchemy, redis; print('✅ Dependencias principales OK')" || (
    echo ❌ Dependencias faltantes. Ejecuta: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Verificar Tesseract
echo 🔍 Verificando Tesseract...
tesseract --version >nul 2>&1 || (
    echo ⚠️  Tesseract no encontrado. Instala Tesseract OCR para mejor funcionalidad.
    echo    Descarga desde https://github.com/UB-Mannheim/tesseract/wiki
)

REM Iniciar aplicación
echo 🚀 Iniciando aplicación...
echo 📖 Documentación: http://localhost:8005/docs
echo 🔍 Health check: http://localhost:8005/health
echo ℹ️  Presiona Ctrl+C para detener
echo.

python main.py
