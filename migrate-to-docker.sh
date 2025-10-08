#!/bin/bash

echo "🔄 Migrando de Desarrollo Local a Docker"
echo "========================================"

# Verificar que estamos en el directorio correcto
if [ ! -f "main.py" ]; then
    echo "❌ No se encuentra main.py. Ejecuta desde el directorio raíz del proyecto."
    exit 1
fi

# 1. Verificar código estable
echo "🔍 Verificando código estable..."
if [ -d ".venv" ]; then
    echo "✅ Entorno virtual encontrado"
    source .venv/bin/activate
    
    # Verificar que no hay errores críticos
    if python -c "import src.app.main" 2>/dev/null; then
        echo "✅ Código importa correctamente"
    else
        echo "❌ Error en el código. Corrige antes de migrar."
        exit 1
    fi
else
    echo "⚠️  Entorno virtual no encontrado. Continuando con verificación básica..."
fi

# 2. Verificar archivos necesarios
echo "📁 Verificando archivos necesarios..."
required_files=("Dockerfile" "docker-compose.yml" "requirements.txt" "src/app/main.py")
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file encontrado"
    else
        echo "❌ $file no encontrado"
        exit 1
    fi
done

# 3. Detener desarrollo local si está corriendo
echo "⏹️ Deteniendo desarrollo local..."
pkill -f "python main.py" 2>/dev/null || echo "No hay procesos locales corriendo"

# 4. Configurar Docker
echo "🐳 Configurando Docker..."

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado. Instala Docker primero."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose no está instalado. Instala Docker Compose primero."
    exit 1
fi

echo "✅ Docker y Docker Compose encontrados"

# 5. Crear directorios necesarios
echo "📁 Creando directorios necesarios..."
mkdir -p uploads outputs data logs ssl
touch uploads/.gitkeep outputs/.gitkeep data/.gitkeep logs/.gitkeep

# 6. Configurar variables de entorno para Docker
echo "📝 Configurando variables de entorno para Docker..."
if [ ! -f ".env" ]; then
    if [ -f "env.example" ]; then
        cp env.example .env
        echo "✅ Archivo .env creado desde env.example"
    else
        echo "⚠️  Archivo env.example no encontrado. Crea .env manualmente."
    fi
fi

# 7. Construir imágenes Docker
echo "🔨 Construyendo imágenes Docker..."
if docker-compose build; then
    echo "✅ Imágenes construidas correctamente"
else
    echo "❌ Error construyendo imágenes"
    exit 1
fi

# 8. Iniciar servicios Docker
echo "🚀 Iniciando servicios Docker..."
if docker-compose up -d; then
    echo "✅ Servicios iniciados"
else
    echo "❌ Error iniciando servicios"
    exit 1
fi

# 9. Esperar a que los servicios estén listos
echo "⏳ Esperando que los servicios estén listos..."
sleep 15

# 10. Verificar funcionamiento
echo "✅ Verificando funcionamiento..."

# Verificar PostgreSQL
echo "🔍 Verificando PostgreSQL..."
if docker-compose exec -T postgres pg_isready -U postgres; then
    echo "✅ PostgreSQL funcionando"
else
    echo "⚠️  PostgreSQL no responde"
fi

# Verificar Redis
echo "🔍 Verificando Redis..."
if docker-compose exec -T redis redis-cli ping | grep -q "PONG"; then
    echo "✅ Redis funcionando"
else
    echo "⚠️  Redis no responde"
fi

# Verificar aplicación
echo "🔍 Verificando aplicación..."
max_attempts=10
attempt=1
while [ $attempt -le $max_attempts ]; do
    if curl -f http://localhost:8005/health >/dev/null 2>&1; then
        echo "✅ Aplicación funcionando"
        break
    else
        echo "⏳ Intento $attempt/$max_attempts - Esperando aplicación..."
        sleep 5
        ((attempt++))
    fi
done

if [ $attempt -gt $max_attempts ]; then
    echo "❌ Aplicación no responde después de $max_attempts intentos"
    echo "📋 Ver logs: docker-compose logs app"
    exit 1
fi

# 11. Mostrar información de migración exitosa
echo ""
echo "🎉 ¡Migración a Docker completada exitosamente!"
echo ""
echo "🌐 URLs importantes:"
echo "   API: http://localhost:8005"
echo "   Documentación: http://localhost:8005/docs"
echo "   Health Check: http://localhost:8005/health"
echo "   Info del Sistema: http://localhost:8005/info"
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
echo "   Estado: docker-compose ps"
echo ""
echo "🧪 Para probar:"
echo "   curl -X POST 'http://localhost:8005/api/v1/upload-optimized' \\"
echo "        -F 'file=@tu-documento.pdf' \\"
echo "        -F 'document_type=factura'"
echo ""

# 12. Mostrar estado de servicios
echo "📊 Estado de servicios:"
docker-compose ps
