#!/bin/bash

echo "🐳 Configurando proyecto con Docker..."

# Crear directorios necesarios
mkdir -p uploads outputs data logs ssl

# Crear archivos .gitkeep para mantener directorios en git
touch uploads/.gitkeep outputs/.gitkeep data/.gitkeep logs/.gitkeep

# Copiar archivo de entorno si no existe
if [ ! -f .env ]; then
    cp .env.example .env
    echo "📝 Archivo .env creado desde .env.example"
fi

# Construir imágenes
echo "🔨 Construyendo imágenes Docker..."
docker-compose build

echo "✅ Configuración completada!"
echo ""
echo "Para iniciar en modo desarrollo:"
echo "docker-compose up -d"
echo ""
echo "Para iniciar en modo producción:"
echo "docker-compose -f docker-compose.prod.yml up -d"
echo ""
echo "Para ver logs:"
echo "docker-compose logs -f app"
echo ""
echo "La API estará disponible en: http://localhost:8005"
echo "Documentación: http://localhost:8005/docs"
