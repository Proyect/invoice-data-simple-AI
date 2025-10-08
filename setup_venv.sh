#!/bin/bash

echo "🐍 Configurando Document Extractor API con Entorno Virtual"
echo "=========================================================="

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no está instalado. Por favor instala Python 3.8+ primero."
    exit 1
fi

echo "✅ Python3 detectado: $(python3 --version)"

# Crear entorno virtual
echo "🔧 Creando entorno virtual..."
python3 -m venv .venv

# Activar entorno virtual
echo "⚡ Activando entorno virtual..."
source .venv/bin/activate

# Actualizar pip
echo "📦 Actualizando pip..."
pip install --upgrade pip

# Instalar dependencias
echo "📚 Instalando dependencias..."
pip install -r requirements.txt

# Instalar modelo de spaCy
echo "🧠 Instalando modelo de spaCy..."
python -m spacy download es_core_news_sm

# Crear directorios necesarios
echo "📁 Creando directorios..."
mkdir -p uploads outputs data logs ssl
touch uploads/.gitkeep outputs/.gitkeep data/.gitkeep logs/.gitkeep

# Configurar variables de entorno
if [ ! -f .env ]; then
    echo "📝 Creando archivo .env..."
    cp env.example .env
    echo "   Edita .env para configurar tus APIs (opcional)"
fi

echo ""
echo "✅ Configuración completada!"
echo ""
echo "🚀 Para activar el entorno virtual:"
echo "   source .venv/bin/activate"
echo ""
echo "🚀 Para iniciar la aplicación:"
echo "   source .venv/bin/activate"
echo "   python main.py"
echo ""
echo "📖 Documentación: http://localhost:8005/docs"
echo "🔍 Health check: http://localhost:8005/health"
echo ""
echo "💡 Comandos útiles:"
echo "   make dev-venv    - Iniciar con entorno virtual"
echo "   make install     - Instalar dependencias"
echo "   make test        - Ejecutar tests"
echo "   make format      - Formatear código"
