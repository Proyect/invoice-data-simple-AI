@echo off
echo 🔧 Solucionando problemas de instalación en Windows
echo ==================================================

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado. Instala Python 3.8+ primero.
    pause
    exit /b 1
)

echo ✅ Python detectado:
python --version

REM Crear entorno virtual si no existe
if not exist ".venv" (
    echo 🔧 Creando entorno virtual...
    python -m venv .venv
)

REM Activar entorno virtual
echo ⚡ Activando entorno virtual...
call .venv\Scripts\activate

REM Actualizar pip y herramientas
echo 📦 Actualizando pip y herramientas...
python -m pip install --upgrade pip
python -m pip install --upgrade wheel setuptools

REM Instalar dependencias mínimas primero
echo 📚 Instalando dependencias mínimas...
pip install -r requirements-venv-minimal.txt

REM Verificar instalación básica
echo 🔍 Verificando instalación básica...
python -c "import fastapi, sqlalchemy; print('✅ Dependencias básicas OK')" || (
    echo ❌ Error en dependencias básicas
    pause
    exit /b 1
)

REM Instalar spaCy
echo 🧠 Instalando spaCy...
python -m spacy download es_core_news_sm

REM Intentar instalar dependencias opcionales
echo 📚 Instalando dependencias opcionales...
pip install pdf2image || echo "⚠️  pdf2image no instalado (opcional)"
pip install opencv-python-headless || echo "⚠️  opencv no instalado (opcional)"
pip install redis || echo "⚠️  redis no instalado (opcional)"
pip install boto3 || echo "⚠️  boto3 no instalado (opcional)"
pip install google-cloud-vision || echo "⚠️  google-cloud-vision no instalado (opcional)"

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
echo ✅ Instalación completada!
echo.
echo 🚀 Para iniciar la aplicación:
echo    .venv\Scripts\activate
echo    python main.py
echo.
echo 📖 Documentación: http://localhost:8005/docs
echo 🔍 Health check: http://localhost:8005/health
echo.
echo 💡 Si hay errores, la aplicación funcionará con funcionalidad limitada.
pause
