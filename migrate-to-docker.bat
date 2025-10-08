@echo off
echo 🔄 Migrando de Desarrollo Local a Docker
echo ========================================

REM Verificar que estamos en el directorio correcto
if not exist "main.py" (
    echo ❌ No se encuentra main.py. Ejecuta desde el directorio raíz del proyecto.
    pause
    exit /b 1
)

REM 1. Verificar código estable
echo 🔍 Verificando código estable...
if exist ".venv" (
    echo ✅ Entorno virtual encontrado
    call .venv\Scripts\activate
    
    REM Verificar que no hay errores críticos
    python -c "import src.app.main" >nul 2>&1
    if errorlevel 1 (
        echo ❌ Error en el código. Corrige antes de migrar.
        pause
        exit /b 1
    ) else (
        echo ✅ Código importa correctamente
    )
) else (
    echo ⚠️  Entorno virtual no encontrado. Continuando con verificación básica...
)

REM 2. Verificar archivos necesarios
echo 📁 Verificando archivos necesarios...
if not exist "Dockerfile" (
    echo ❌ Dockerfile no encontrado
    pause
    exit /b 1
)
if not exist "docker-compose.yml" (
    echo ❌ docker-compose.yml no encontrado
    pause
    exit /b 1
)
if not exist "requirements.txt" (
    echo ❌ requirements.txt no encontrado
    pause
    exit /b 1
)
if not exist "src\app\main.py" (
    echo ❌ src\app\main.py no encontrado
    pause
    exit /b 1
)
echo ✅ Todos los archivos necesarios encontrados

REM 3. Detener desarrollo local si está corriendo
echo ⏹️ Deteniendo desarrollo local...
taskkill /f /im python.exe >nul 2>&1 || echo No hay procesos locales corriendo

REM 4. Configurar Docker
echo 🐳 Configurando Docker...

REM Verificar Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker no está instalado. Instala Docker primero.
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose no está instalado. Instala Docker Compose primero.
    pause
    exit /b 1
)

echo ✅ Docker y Docker Compose encontrados

REM 5. Crear directorios necesarios
echo 📁 Creando directorios necesarios...
mkdir uploads 2>nul
mkdir outputs 2>nul
mkdir data 2>nul
mkdir logs 2>nul
mkdir ssl 2>nul

echo. > uploads\.gitkeep
echo. > outputs\.gitkeep
echo. > data\.gitkeep
echo. > logs\.gitkeep

REM 6. Configurar variables de entorno para Docker
echo 📝 Configurando variables de entorno para Docker...
if not exist ".env" (
    if exist "env.example" (
        copy env.example .env >nul
        echo ✅ Archivo .env creado desde env.example
    ) else (
        echo ⚠️  Archivo env.example no encontrado. Crea .env manualmente.
    )
)

REM 7. Construir imágenes Docker
echo 🔨 Construyendo imágenes Docker...
docker-compose build
if errorlevel 1 (
    echo ❌ Error construyendo imágenes
    pause
    exit /b 1
)
echo ✅ Imágenes construidas correctamente

REM 8. Iniciar servicios Docker
echo 🚀 Iniciando servicios Docker...
docker-compose up -d
if errorlevel 1 (
    echo ❌ Error iniciando servicios
    pause
    exit /b 1
)
echo ✅ Servicios iniciados

REM 9. Esperar a que los servicios estén listos
echo ⏳ Esperando que los servicios estén listos...
timeout /t 15 /nobreak >nul

REM 10. Verificar funcionamiento
echo ✅ Verificando funcionamiento...

REM Verificar PostgreSQL
echo 🔍 Verificando PostgreSQL...
docker-compose exec -T postgres pg_isready -U postgres >nul 2>&1
if errorlevel 1 (
    echo ⚠️  PostgreSQL no responde
) else (
    echo ✅ PostgreSQL funcionando
)

REM Verificar Redis
echo 🔍 Verificando Redis...
docker-compose exec -T redis redis-cli ping | findstr "PONG" >nul
if errorlevel 1 (
    echo ⚠️  Redis no responde
) else (
    echo ✅ Redis funcionando
)

REM Verificar aplicación
echo 🔍 Verificando aplicación...
set /a attempt=1
set /a max_attempts=10
:check_app
curl -f http://localhost:8005/health >nul 2>&1
if not errorlevel 1 (
    echo ✅ Aplicación funcionando
    goto app_ready
)
if %attempt% lss %max_attempts% (
    echo ⏳ Intento %attempt%/%max_attempts% - Esperando aplicación...
    timeout /t 5 /nobreak >nul
    set /a attempt+=1
    goto check_app
) else (
    echo ❌ Aplicación no responde después de %max_attempts% intentos
    echo 📋 Ver logs: docker-compose logs app
    pause
    exit /b 1
)

:app_ready

REM 11. Mostrar información de migración exitosa
echo.
echo 🎉 ¡Migración a Docker completada exitosamente!
echo.
echo 🌐 URLs importantes:
echo    API: http://localhost:8005
echo    Documentación: http://localhost:8005/docs
echo    Health Check: http://localhost:8005/health
echo    Info del Sistema: http://localhost:8005/info
echo.
echo 🗄️ Base de datos:
echo    PgAdmin: http://localhost:5050 (admin@admin.com / admin)
echo    PostgreSQL: localhost:5432
echo    Redis: localhost:6379
echo.
echo 📋 Comandos útiles:
echo    Ver logs: docker-compose logs -f app
echo    Detener: docker-compose down
echo    Reiniciar: docker-compose restart app
echo    Estado: docker-compose ps
echo.

REM 12. Mostrar estado de servicios
echo 📊 Estado de servicios:
docker-compose ps

pause
