#!/bin/bash

echo "🚀 Iniciando Document Extractor API con Entorno Virtual"
echo "======================================================"

# Verificar si existe el entorno virtual
if [ ! -d ".venv" ]; then
    echo "❌ Entorno virtual no encontrado. Ejecuta primero: ./setup_venv.sh"
    exit 1
fi

# Activar entorno virtual
echo "⚡ Activando entorno virtual..."
source .venv/bin/activate

# Verificar instalación
echo "🔍 Verificando instalación..."
python -c "import fastapi, sqlalchemy, redis; print('✅ Dependencias principales OK')" || {
    echo "❌ Dependencias faltantes. Ejecuta: pip install -r requirements.txt"
    exit 1
}

# Verificar Tesseract
echo "🔍 Verificando Tesseract..."
tesseract --version > /dev/null 2>&1 || {
    echo "⚠️  Tesseract no encontrado. Instala Tesseract OCR para mejor funcionalidad."
    echo "   Ubuntu/Debian: sudo apt install tesseract-ocr"
    echo "   macOS: brew install tesseract"
    echo "   Windows: Descarga desde https://github.com/UB-Mannheim/tesseract/wiki"
}

# Iniciar aplicación
echo "🚀 Iniciando aplicación..."
echo "📖 Documentación: http://localhost:8005/docs"
echo "🔍 Health check: http://localhost:8005/health"
echo "ℹ️  Presiona Ctrl+C para detener"
echo ""

python main.py
