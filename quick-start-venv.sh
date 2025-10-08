#!/bin/bash

echo "🐍 Document Extractor API - Inicio Rápido con Entorno Virtual"
echo "============================================================"

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no está instalado. Por favor instala Python 3.8+ primero."
    exit 1
fi

echo "✅ Python3 detectado: $(python3 --version)"

# Verificar si ya existe entorno virtual
if [ -d ".venv" ]; then
    echo "✅ Entorno virtual encontrado"
else
    echo "🔧 Configurando entorno virtual por primera vez..."
    chmod +x setup_venv.sh
    ./setup_venv.sh
fi

# Activar entorno virtual
echo "⚡ Activando entorno virtual..."
source .venv/bin/activate

# Verificar Tesseract
echo "🔍 Verificando Tesseract..."
if tesseract --version > /dev/null 2>&1; then
    echo "✅ Tesseract encontrado"
else
    echo "⚠️  Tesseract no encontrado. Instala para mejor funcionalidad:"
    echo "   Ubuntu/Debian: sudo apt install tesseract-ocr"
    echo "   macOS: brew install tesseract"
    echo "   Windows: https://github.com/UB-Mannheim/tesseract/wiki"
fi

# Verificar PostgreSQL (opcional)
echo "🔍 Verificando PostgreSQL..."
if command -v psql &> /dev/null; then
    echo "✅ PostgreSQL encontrado (opcional para usar SQLite)"
else
    echo "ℹ️  PostgreSQL no encontrado - usando SQLite por defecto"
fi

# Verificar Redis (opcional)
echo "🔍 Verificando Redis..."
if command -v redis-server &> /dev/null; then
    echo "✅ Redis encontrado"
else
    echo "ℹ️  Redis no encontrado - funcionalidad de cache limitada"
fi

# Iniciar aplicación
echo ""
echo "🚀 Iniciando aplicación..."
echo "📖 Documentación: http://localhost:8005/docs"
echo "🔍 Health check: http://localhost:8005/health"
echo "ℹ️  Presiona Ctrl+C para detener"
echo ""

python main.py
