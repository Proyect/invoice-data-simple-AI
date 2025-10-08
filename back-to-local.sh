#!/bin/bash

echo "🔄 Regresando a Desarrollo Local"
echo "==============================="

# 1. Detener Docker
echo "⏹️ Deteniendo servicios Docker..."
if command -v docker-compose &> /dev/null; then
    docker-compose down
    echo "✅ Servicios Docker detenidos"
else
    echo "⚠️  Docker Compose no encontrado"
fi

# 2. Verificar entorno virtual
echo "🐍 Verificando entorno virtual..."
if [ -d ".venv" ]; then
    echo "✅ Entorno virtual encontrado"
else
    echo "❌ Entorno virtual no encontrado. Ejecuta: make setup-venv"
    exit 1
fi

# 3. Activar entorno virtual
echo "⚡ Activando entorno virtual..."
source .venv/bin/activate

# 4. Verificar dependencias
echo "📚 Verificando dependencias..."
if python -c "import fastapi, sqlalchemy" 2>/dev/null; then
    echo "✅ Dependencias principales OK"
else
    echo "⚠️  Dependencias faltantes. Ejecutando: pip install -r requirements-venv.txt"
    pip install -r requirements-venv.txt
fi

# 5. Configurar variables de entorno para local
echo "📝 Configurando para desarrollo local..."
if [ -f ".env" ]; then
    # Hacer backup del .env actual
    cp .env .env.docker.backup
    echo "✅ Backup de .env guardado como .env.docker.backup"
fi

# Crear .env para desarrollo local
cat > .env << EOF
# Configuración para desarrollo local
APP_NAME=Document Extractor API - Dev
DEBUG=True
HOST=0.0.0.0
PORT=8005

# SQLite para desarrollo rápido
DATABASE_URL=sqlite:///./data/documents.db

# Redis local (opcional)
REDIS_URL=redis://localhost:6379
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Directorios
UPLOAD_DIR=uploads
OUTPUT_DIR=outputs

# Tesseract local
TESSERACT_CMD=

# Configuración OCR
GOOGLE_VISION_DAILY_LIMIT=200
AWS_TEXTRACT_DAILY_LIMIT=100
TESSERACT_CONFIDENCE_THRESHOLD=0.7

# Configuración LLM (opcional)
OPENAI_API_KEY=
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=1000
OPENAI_TEMPERATURE=0

# Configuración AWS (opcional)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1

# Configuración Google Cloud (opcional)
GOOGLE_APPLICATION_CREDENTIALS=

# Procesamiento asíncrono
RQ_WORKER_TIMEOUT=600
RQ_QUEUE_NAME=document_processing
EOF

echo "✅ Archivo .env configurado para desarrollo local"

# 6. Crear directorio de datos si no existe
echo "📁 Preparando directorios..."
mkdir -p uploads outputs data logs
touch uploads/.gitkeep outputs/.gitkeep data/.gitkeep logs/.gitkeep

# 7. Verificar Tesseract
echo "🔍 Verificando Tesseract..."
if tesseract --version > /dev/null 2>&1; then
    echo "✅ Tesseract encontrado"
else
    echo "⚠️  Tesseract no encontrado. Instala para mejor funcionalidad:"
    echo "   Ubuntu/Debian: sudo apt install tesseract-ocr"
    echo "   macOS: brew install tesseract"
    echo "   Windows: https://github.com/UB-Mannheim/tesseract/wiki"
fi

# 8. Verificar PostgreSQL (opcional)
echo "🔍 Verificando PostgreSQL..."
if command -v psql &> /dev/null; then
    echo "✅ PostgreSQL encontrado (opcional para usar SQLite)"
else
    echo "ℹ️  PostgreSQL no encontrado - usando SQLite por defecto"
fi

# 9. Verificar Redis (opcional)
echo "🔍 Verificando Redis..."
if command -v redis-server &> /dev/null; then
    echo "✅ Redis encontrado"
else
    echo "ℹ️  Redis no encontrado - funcionalidad de cache limitada"
fi

# 10. Iniciar aplicación local
echo ""
echo "🚀 Iniciando desarrollo local..."
echo "📖 Documentación: http://localhost:8005/docs"
echo "🔍 Health check: http://localhost:8005/health"
echo "ℹ️  Presiona Ctrl+C para detener"
echo ""

python main.py
