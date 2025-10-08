#!/bin/bash

echo "🚀 Document Extractor API - Optimized - Inicio Rápido"
echo "====================================================="

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado. Por favor instala Docker primero."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose no está instalado. Por favor instala Docker Compose primero."
    exit 1
fi

echo "✅ Docker detectado"

# Configurar proyecto
echo "🔧 Configurando proyecto..."
mkdir -p uploads outputs data logs ssl
touch uploads/.gitkeep outputs/.gitkeep data/.gitkeep logs/.gitkeep

if [ ! -f .env ]; then
    cp env.example .env
    echo "📝 Archivo .env creado"
fi

# Construir y ejecutar
echo "🔨 Construyendo imágenes..."
docker-compose build

echo "🚀 Iniciando aplicación..."
docker-compose up -d

# Esperar a que la aplicación esté lista
echo "⏳ Esperando que la aplicación esté lista..."
sleep 15

# Verificar que funciona
if curl -f http://localhost:8005/health &> /dev/null; then
    echo ""
    echo "✅ ¡Aplicación iniciada correctamente!"
    echo ""
    echo "🌐 URLs importantes:"
    echo "   API: http://localhost:8005"
    echo "   Docs: http://localhost:8005/docs"
    echo "   Health: http://localhost:8005/health"
    echo "   Info: http://localhost:8005/info"
    echo ""
    echo "🗄️ Base de datos:"
    echo "   PgAdmin: http://localhost:5050 (admin@admin.com / admin)"
    echo "   PostgreSQL: localhost:5432"
    echo "   Redis: localhost:6379"
    echo ""
    echo "📋 Comandos útiles:"
    echo "   Ver logs: docker-compose logs -f app"
    echo "   Detener: docker-compose down"
    echo "   Reiniciar: docker-compose restart app"
    echo "   Stats: curl http://localhost:8005/api/v1/queue/stats"
    echo ""
    echo "🎯 Para probar:"
    echo "   curl -X POST 'http://localhost:8005/api/v1/upload-optimized' \\"
    echo "        -F 'file=@tu-documento.pdf' \\"
    echo "        -F 'document_type=factura'"
else
    echo "❌ Error: La aplicación no responde"
    echo "📋 Ver logs: docker-compose logs app"
    echo "🔍 Verificar servicios: docker-compose ps"
fi
