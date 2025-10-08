@echo off
echo 🐍 Configurando Document Extractor API con Entorno Virtual
echo ==========================================================

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado. Por favor instala Python 3.8+ primero.
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

REM Actualizar pip
echo 📦 Actualizando pip...
python -m pip install --upgrade pip

REM Instalar dependencias
echo 📚 Instalando dependencias...
pip install -r requirements.txt

REM Instalar modelo de spaCy
echo 🧠 Instalando modelo de spaCy...
python -m spacy download es_core_news_sm

REM Crear directorios necesarios
echo 📁 Creando directorios...
mkdir uploads 2>nul
mkdir outputs 2>nul
mkdir data 2>nul
mkdir logs 2>nul
mkdir ssl 2>nul

echo. > uploads\.gitkeep
echo. > outputs\.gitkeep
echo. > data\.gitkeep
echo. > logs\.gitkeep

REM Configurar variables de entorno
if not exist .env (
    echo 📝 Creando archivo .env...
    copy env.example .env
    echo    Edita .env para configurar tus APIs (opcional)
)

echo.
echo ✅ Configuración completada!
echo.
echo 🚀 Para activar el entorno virtual:
echo    .venv\Scripts\activate
echo.
echo 🚀 Para iniciar la aplicación:
echo    .venv\Scripts\activate
echo    python main.py
echo.
echo 📖 Documentación: http://localhost:8005/docs
echo 🔍 Health check: http://localhost:8005/health
echo.
echo 💡 Comandos útiles:
echo    make dev-venv    - Iniciar con entorno virtual
echo    make install     - Instalar dependencias
echo    make test        - Ejecutar tests
echo    make format      - Formatear código
pause
