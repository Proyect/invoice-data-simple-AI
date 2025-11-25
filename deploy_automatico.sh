#!/bin/bash

# 🚀 Script de Deploy Automático - Document Extractor
# Ejecuta todo el proceso de deploy paso a paso

set -e  # Salir si hay errores

echo "🚀 INICIANDO DEPLOY AUTOMÁTICO DE DOCUMENT EXTRACTOR"
echo "=================================================="
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar pasos
show_step() {
    echo -e "${BLUE}📋 PASO $1: $2${NC}"
    echo "----------------------------------------"
}

# Función para mostrar éxito
show_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Función para mostrar advertencia
show_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Función para mostrar error
show_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar prerequisitos
show_step "1" "Verificando prerequisitos"

# Verificar Git
if ! command -v git &> /dev/null; then
    show_error "Git no está instalado"
    exit 1
fi
show_success "Git instalado"

# Verificar Node.js (para frontend)
if ! command -v node &> /dev/null; then
    show_warning "Node.js no encontrado - se omitirá deploy de frontend"
    DEPLOY_FRONTEND=false
else
    show_success "Node.js instalado"
    DEPLOY_FRONTEND=true
fi

# Verificar Python
if ! command -v python3 &> /dev/null; then
    show_error "Python 3 no está instalado"
    exit 1
fi
show_success "Python 3 instalado"

echo ""

# Configurar Git si no está configurado
show_step "2" "Configurando Git"
if [ -z "$(git config --global user.name)" ]; then
    read -p "Ingresa tu nombre para Git: " git_name
    git config --global user.name "$git_name"
fi

if [ -z "$(git config --global user.email)" ]; then
    read -p "Ingresa tu email para Git: " git_email
    git config --global user.email "$git_email"
fi
show_success "Git configurado"

echo ""

# Preparar archivos de producción
show_step "3" "Preparando archivos de producción"

# Crear Dockerfile de producción
cat > Dockerfile.production << 'EOF'
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-spa \
    poppler-utils \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download es_core_news_sm

# Copiar código
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini .

# Crear directorios
RUN mkdir -p uploads outputs data logs
RUN chown -R appuser:appuser /app

USER appuser
EXPOSE 8005

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8005/health || exit 1

CMD ["python", "-m", "uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8005"]
EOF

show_success "Dockerfile.production creado"

# Crear railway.json
cat > railway.json << 'EOF'
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile.production"
  },
  "deploy": {
    "startCommand": "python -m uvicorn src.app.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 30,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
EOF

show_success "railway.json creado"

# Crear .gitignore de producción
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Project specific
uploads/
outputs/
data/
logs/
*.log

# Credentials
google-service-account.json
*.pem
*.key
production-credentials.txt

# Frontend
frontend/node_modules/
frontend/build/
frontend/.env.local
frontend/.env.production.local

# Database
*.db
*.sqlite
*.sqlite3
EOF

show_success "Archivos de configuración creados"

echo ""

# Crear configuración de producción
show_step "4" "Creando configuración de producción"

cat > .env.production.template << 'EOF'
# ===========================================
# CONFIGURACIÓN DE PRODUCCIÓN
# ===========================================

APP_NAME=Document Extractor API - Production
DEBUG=False
HOST=0.0.0.0
PORT=8005

# IMPORTANTE: Reemplazar con tus valores reales
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROYECTO].supabase.co:5432/postgres
REDIS_URL=rediss://:[PASSWORD]@[HOST].upstash.io:6380
OPENAI_API_KEY=sk-proj-[TU_KEY]
GOOGLE_APPLICATION_CREDENTIALS=/app/google-service-account.json

# Seguridad (generar clave segura)
SECRET_KEY=CAMBIAR-POR-CLAVE-SEGURA-DE-32-CARACTERES
ALGORITHM=HS256

# Configuración de producción
RATE_LIMIT_PER_MINUTE=60
TESSERACT_CONFIDENCE_THRESHOLD=0.75
UPLOAD_DIR=uploads
OUTPUT_DIR=outputs
EOF

show_success "Template de configuración creado"

echo ""

# Preparar frontend si existe
if [ "$DEPLOY_FRONTEND" = true ] && [ -d "frontend" ]; then
    show_step "5" "Preparando frontend para producción"
    
    cd frontend
    
    # Crear .env.production para frontend
    cat > .env.production << 'EOF'
REACT_APP_API_URL=https://TU-PROYECTO.railway.app/api/v1
REACT_APP_ENV=production
GENERATE_SOURCEMAP=false
EOF
    
    # Instalar dependencias si no existen
    if [ ! -d "node_modules" ]; then
        npm install
    fi
    
    # Build de producción
    npm run build
    
    cd ..
    show_success "Frontend preparado"
else
    show_warning "Frontend no encontrado o Node.js no disponible"
fi

echo ""

# Crear script de verificación post-deploy
show_step "6" "Creando scripts de verificación"

cat > verify_deploy.py << 'EOF'
#!/usr/bin/env python3
"""
Script para verificar que el deploy funcionó correctamente
"""
import requests
import sys
import time

def test_endpoint(url, name, expected_status=200):
    """Test un endpoint específico"""
    try:
        print(f"🔍 Testing {name}...")
        response = requests.get(url, timeout=10)
        
        if response.status_code == expected_status:
            print(f"✅ {name}: OK ({response.status_code})")
            return True
        else:
            print(f"❌ {name}: Error {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {name}: Connection error - {str(e)}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Uso: python verify_deploy.py <BASE_URL>")
        print("Ejemplo: python verify_deploy.py https://mi-proyecto.railway.app")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    
    print(f"🚀 Verificando deploy en: {base_url}")
    print("=" * 50)
    
    # Lista de endpoints a verificar
    tests = [
        (f"{base_url}/health", "Health Check"),
        (f"{base_url}/", "Root Endpoint"),
        (f"{base_url}/docs", "API Documentation"),
        (f"{base_url}/api/v1/upload-flexible/methods", "Available Methods"),
    ]
    
    results = []
    for url, name in tests:
        result = test_endpoint(url, name)
        results.append(result)
        time.sleep(1)  # Pausa entre requests
    
    print("\n" + "=" * 50)
    successful = sum(results)
    total = len(results)
    
    if successful == total:
        print(f"🎉 Deploy exitoso! {successful}/{total} tests pasaron")
        print(f"🌐 Tu API está funcionando en: {base_url}")
        print(f"📚 Documentación disponible en: {base_url}/docs")
        return 0
    else:
        print(f"⚠️  Deploy parcial: {successful}/{total} tests pasaron")
        print("🔧 Revisa los logs de Railway para más detalles")
        return 1

if __name__ == "__main__":
    sys.exit(main())
EOF

chmod +x verify_deploy.py
show_success "Script de verificación creado"

echo ""

# Commit inicial
show_step "7" "Preparando commit inicial"

git add .
git commit -m "feat: configuración inicial de producción

- Dockerfile optimizado para producción
- Configuración de Railway
- Scripts de verificación
- Templates de configuración
- Frontend build ready" || show_warning "Ya hay cambios commiteados"

show_success "Cambios commiteados"

echo ""

# Instrucciones finales
show_step "8" "Instrucciones finales"

echo ""
echo "🎯 PRÓXIMOS PASOS PARA COMPLETAR EL DEPLOY:"
echo ""
echo "1️⃣  CONFIGURAR SERVICIOS CLOUD:"
echo "   • Supabase: https://supabase.com/ (PostgreSQL)"
echo "   • Upstash: https://upstash.com/ (Redis)"  
echo "   • OpenAI: https://platform.openai.com/ (LLM)"
echo "   • Google Cloud: https://console.cloud.google.com/ (Vision API)"
echo ""
echo "2️⃣  DEPLOY EN RAILWAY:"
echo "   • Ve a: https://railway.app/"
echo "   • Login with GitHub"
echo "   • New Project → Deploy from GitHub repo"
echo "   • Configura variables de entorno usando .env.production.template"
echo ""
echo "3️⃣  DEPLOY FRONTEND EN VERCEL (si tienes frontend):"
echo "   • Ve a: https://vercel.com/"
echo "   • Import Git Repository"
echo "   • Root Directory: frontend"
echo ""
echo "4️⃣  VERIFICAR DEPLOY:"
echo "   python verify_deploy.py https://tu-proyecto.railway.app"
echo ""
echo "📋 ARCHIVOS CREADOS:"
echo "   • Dockerfile.production - Container optimizado"
echo "   • railway.json - Configuración de Railway"
echo "   • .env.production.template - Variables de entorno"
echo "   • verify_deploy.py - Script de verificación"
echo "   • .gitignore - Archivos a ignorar"
echo ""
echo "📚 DOCUMENTACIÓN COMPLETA:"
echo "   • README.md - Guía principal del proyecto"
echo ""
echo "🎉 ¡PREPARACIÓN COMPLETADA!"
echo "   Tiempo estimado para completar deploy: 30-45 minutos"
echo "   Costo: $0/mes por los primeros 6 meses"

# Preguntar si quiere abrir URLs
echo ""
read -p "¿Abrir Railway en el navegador para continuar? (y/n): " open_railway
if [ "$open_railway" = "y" ]; then
    if command -v xdg-open &> /dev/null; then
        xdg-open "https://railway.app/"
    elif command -v open &> /dev/null; then
        open "https://railway.app/"
    else
        echo "Abre manualmente: https://railway.app/"
    fi
fi

echo ""
echo "✨ Deploy preparation completed successfully!"

















