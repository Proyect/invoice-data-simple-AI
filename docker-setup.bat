@echo off
echo 🐳 Configurando proyecto con Docker...

REM Crear directorios necesarios
mkdir uploads 2>nul
mkdir outputs 2>nul
mkdir data 2>nul
mkdir logs 2>nul
mkdir ssl 2>nul

REM Crear archivos .gitkeep para mantener directorios en git
echo. > uploads\.gitkeep
echo. > outputs\.gitkeep
echo. > data\.gitkeep
echo. > logs\.gitkeep

REM Copiar archivo de entorno si no existe
if not exist .env (
    copy .env.example .env
    echo 📝 Archivo .env creado desde .env.example
)

REM Construir imágenes
echo 🔨 Construyendo imágenes Docker...
docker-compose build

echo.
echo ✅ Configuración completada!
echo.
echo Para iniciar en modo desarrollo:
echo docker-compose up -d
echo.
echo Para iniciar en modo producción:
echo docker-compose -f docker-compose.prod.yml up -d
echo.
echo Para ver logs:
echo docker-compose logs -f app
echo.
echo La API estará disponible en: http://localhost:8005
echo Documentación: http://localhost:8005/docs
pause
