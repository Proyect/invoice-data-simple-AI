@echo off
echo 🐍 Configurando Document Extractor API para Windows
echo ==================================================

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado. Instala Python 3.8+ primero.
    echo    Descarga desde: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python detectado:
python --version

REM Crear entorno virtual
echo 🔧 Creando entorno virtual...
python -m venv .venv

REM Activar entorno virtual
echo ⚡ Activando entorno virtual...
call .venv\Scripts\activate

REM Actualizar pip y herramientas
echo 📦 Actualizando pip y herramientas...
python -m pip install --upgrade pip
python -m pip install --upgrade wheel setuptools

REM Instalar dependencias básicas
echo 📚 Instalando dependencias básicas...
pip install fastapi==0.104.1
pip install uvicorn[standard]==0.24.0
pip install python-multipart==0.0.6
pip install pydantic==2.5.0
pip install pydantic-settings==2.1.0
pip install python-dotenv==1.0.0
pip install aiofiles==23.2.1
pip install sqlalchemy==2.0.23
pip install alembic==1.13.1

REM Instalar OCR básico
echo 🔍 Instalando OCR básico...
pip install pytesseract==0.3.10
pip install pillow==10.1.0

REM Instalar dependencias de desarrollo
echo 🛠️ Instalando herramientas de desarrollo...
pip install pytest==7.4.3
pip install pytest-asyncio==0.21.1
pip install black==23.11.0
pip install isort==5.12.0

REM Intentar instalar dependencias opcionales
echo 📚 Instalando dependencias opcionales...
pip install pdf2image || echo "⚠️  pdf2image no instalado (opcional)"
pip install redis || echo "⚠️  redis no instalado (opcional)"
pip install pandas || echo "⚠️  pandas no instalado (opcional)"

REM Instalar spaCy
echo 🧠 Instalando spaCy...
python -m spacy download es_core_news_sm

REM Crear directorios necesarios
echo 📁 Creando directorios...
mkdir uploads 2>nul
mkdir outputs 2>nul
mkdir data 2>nul
mkdir logs 2>nul

echo. > uploads\.gitkeep
echo. > outputs\.gitkeep
echo. > data\.gitkeep
echo. > logs\.gitkeep

REM Configurar variables de entorno
if not exist ".env" (
    echo 📝 Creando archivo .env...
    echo # Configuración para desarrollo local > .env
    echo APP_NAME=Document Extractor API - Dev >> .env
    echo DEBUG=True >> .env
    echo HOST=0.0.0.0 >> .env
    echo PORT=8005 >> .env
    echo. >> .env
    echo # SQLite para desarrollo rápido >> .env
    echo DATABASE_URL=sqlite:///./data/documents.db >> .env
    echo. >> .env
    echo # Directorios >> .env
    echo UPLOAD_DIR=uploads >> .env
    echo OUTPUT_DIR=outputs >> .env
    echo. >> .env
    echo # Tesseract >> .env
    echo TESSERACT_CMD= >> .env
    echo. >> .env
    echo # Configuración OCR >> .env
    echo TESSERACT_CONFIDENCE_THRESHOLD=0.7 >> .env
)

echo.
echo ✅ Configuración completada!
echo.
echo 🚀 Para iniciar la aplicación:
echo    .venv\Scripts\activate
echo    python main.py
echo.
echo 📖 Documentación: http://localhost:8005/docs
echo 🔍 Health check: http://localhost:8005/health
echo.
echo 💡 La aplicación funcionará con funcionalidad básica.
echo    Para funcionalidad completa, instala Tesseract OCR.
pause
