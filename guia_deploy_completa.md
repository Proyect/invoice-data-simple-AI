# 🚀 Guía Completa de Deploy - Document Extractor

## 📋 Prerequisitos

### Lo que necesitas antes de empezar:
- ✅ Cuenta de GitHub (para código)
- ✅ Tarjeta de crédito/débito (para servicios cloud - no se cobra en tier gratuito)
- ✅ Teléfono móvil (para verificaciones)
- ✅ 30-45 minutos de tiempo

---

# FASE 1: PREPARACIÓN DEL CÓDIGO

## Paso 1.1: Preparar el Repositorio
```bash
# Si no tienes Git configurado
git config --global user.name "Tu Nombre"
git config --global user.email "tu@email.com"

# Crear repositorio en GitHub (o usar existente)
# Ve a https://github.com/new
# Nombre: document-extractor-production

# Clonar y preparar
git clone https://github.com/tu-usuario/document-extractor-production.git
cd document-extractor-production

# Copiar archivos del proyecto actual
cp -r /ruta/al/proyecto/actual/* .

# Crear estructura de deploy
mkdir -p deploy/scripts deploy/configs
```

## Paso 1.2: Configurar Archivos de Deploy
```bash
# Crear archivo de configuración de producción
cp config_optimo.env .env.production

# Crear Dockerfile optimizado para producción
cat > Dockerfile.production << 'EOF'
FROM python:3.11-slim

# Variables de entorno
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

# Copiar requirements y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Descargar modelo de spaCy
RUN python -m spacy download es_core_news_sm

# Copiar código
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini .

# Crear directorios necesarios
RUN mkdir -p uploads outputs data logs
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8005

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8005/health || exit 1

CMD ["python", "-m", "uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8005"]
EOF
```

---

# FASE 2: CONFIGURAR SERVICIOS CLOUD

## Paso 2.1: Supabase (Base de Datos) 🏆

### Registro y Configuración:
1. **Ve a https://supabase.com/**
2. **Clic en "Start your project"**
3. **Sign up with GitHub** (recomendado)
4. **New Project:**
   - Organization: Personal (o crear nueva)
   - Name: `document-extractor-prod`
   - Database Password: `[genera una segura]`
   - Region: `East US` (más cercana)
5. **Esperar 2-3 minutos** hasta que esté listo
6. **Settings → Database:**
   - Copiar "Connection string"
   - Formato: `postgresql://postgres:[password]@db.[proyecto].supabase.co:5432/postgres`

### Configurar Tablas:
```sql
-- Ejecutar en Supabase SQL Editor
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Crear tabla de documentos
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    mime_type VARCHAR(100),
    raw_text TEXT,
    extracted_data JSONB,
    confidence_score INTEGER,
    ocr_provider VARCHAR(50),
    ocr_cost VARCHAR(20),
    processing_time VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX idx_documents_filename ON documents(filename);
CREATE INDEX idx_documents_created_at ON documents(created_at DESC);
CREATE INDEX idx_documents_confidence ON documents(confidence_score);

-- Tabla de usuarios (si usas autenticación)
CREATE TABLE users (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    is_superuser BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Paso 2.2: Upstash (Redis Cache) 🏆

### Registro y Configuración:
1. **Ve a https://upstash.com/**
2. **Sign up** (con GitHub o email)
3. **Create Database:**
   - Name: `document-extractor-cache`
   - Type: `Redis`
   - Region: `US-East-1` (Virginia)
   - Plan: `Free` (10K requests/day)
4. **Copiar credenciales:**
   - Redis URL (TLS): `rediss://:[password]@[host].upstash.io:6380`

## Paso 2.3: OpenAI (LLM) 🏆

### Registro y API Key:
1. **Ve a https://platform.openai.com/**
2. **Sign up** y **verificar teléfono**
3. **API Keys → Create new secret key:**
   - Name: `document-extractor-prod`
   - Copiar key (empieza con `sk-proj-`)
4. **Billing → Add payment method** (para después del crédito gratuito)

## Paso 2.4: Google Cloud Vision (OCR) 🏆

### Registro y Configuración:
1. **Ve a https://console.cloud.google.com/**
2. **Crear cuenta** (necesita tarjeta, $300 créditos gratis)
3. **Nuevo Proyecto:**
   - Name: `document-extractor-prod`
   - ID: `doc-extractor-[random]`
4. **Habilitar Vision API:**
   - APIs & Services → Library
   - Buscar "Cloud Vision API" → Enable
5. **Crear Service Account:**
   - IAM & Admin → Service Accounts
   - Create Service Account:
     - Name: `document-extractor-sa`
     - Role: `Cloud Vision API User`
   - Create Key → JSON → Download
   - Guardar como `google-service-account.json`

---

# FASE 3: DEPLOY DEL BACKEND

## Paso 3.1: Railway (Hosting) 🏆

### Configuración Inicial:
1. **Ve a https://railway.app/**
2. **Login with GitHub**
3. **New Project → Deploy from GitHub repo**
4. **Conectar tu repositorio:** `document-extractor-production`

### Configurar Variables de Entorno:
```bash
# En Railway Dashboard → Variables
APP_NAME=Document Extractor API - Production
DEBUG=False
HOST=0.0.0.0
PORT=8005

# Base de datos (de Supabase)
DATABASE_URL=postgresql://postgres:[password]@db.[proyecto].supabase.co:5432/postgres

# Redis (de Upstash)
REDIS_URL=rediss://:[password]@[host].upstash.io:6380
REDIS_HOST=[host].upstash.io
REDIS_PORT=6380

# OpenAI
OPENAI_API_KEY=sk-proj-[tu-key]
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=800

# Google Vision (subir archivo JSON como variable)
GOOGLE_APPLICATION_CREDENTIALS=/app/google-service-account.json

# Seguridad
SECRET_KEY=[generar-clave-segura-32-caracteres]
ALGORITHM=HS256

# Límites de producción
RATE_LIMIT_PER_MINUTE=60
TESSERACT_CONFIDENCE_THRESHOLD=0.75
```

### Subir Credenciales de Google:
```bash
# En Railway, crear variable de entorno especial
# Variable name: GOOGLE_SERVICE_ACCOUNT_JSON
# Value: [pegar todo el contenido del archivo JSON]
```

### Configurar Build:
```bash
# Railway detecta automáticamente Python
# Pero puedes crear railway.json para control fino:
cat > railway.json << 'EOF'
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile.production"
  },
  "deploy": {
    "startCommand": "python -m uvicorn src.app.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 30
  }
}
EOF
```

## Paso 3.2: Deploy Automático
```bash
# Commit y push para trigger deploy
git add .
git commit -m "feat: configuración de producción"
git push origin main

# Railway detecta el push y hace deploy automático
# Ver logs en Railway Dashboard
```

---

# FASE 4: DEPLOY DEL FRONTEND

## Paso 4.1: Preparar Frontend para Producción
```bash
cd frontend

# Configurar variables de entorno de producción
cat > .env.production << 'EOF'
REACT_APP_API_URL=https://tu-app.railway.app/api/v1
REACT_APP_ENV=production
GENERATE_SOURCEMAP=false
EOF

# Optimizar package.json
npm install --production
npm run build
```

## Paso 4.2: Vercel (Frontend Hosting) 🏆

### Deploy del Frontend:
1. **Ve a https://vercel.com/**
2. **Sign up with GitHub**
3. **Import Git Repository:**
   - Seleccionar tu repo
   - Root Directory: `frontend`
   - Framework: `Create React App`
4. **Environment Variables:**
   ```
   REACT_APP_API_URL=https://tu-backend.railway.app/api/v1
   ```
5. **Deploy** (automático)

---

# FASE 5: CONFIGURACIÓN DE DOMINIO Y SSL

## Paso 5.1: Dominio Personalizado (Opcional)
```bash
# Si tienes dominio propio:
# 1. En Railway: Settings → Domains → Add Custom Domain
# 2. En Vercel: Settings → Domains → Add Domain
# 3. Configurar DNS:
#    - Backend: CNAME api.tudominio.com → railway-url
#    - Frontend: CNAME www.tudominio.com → vercel-url
```

## Paso 5.2: Configurar CORS para Producción
```python
# En src/app/main.py, actualizar CORS:
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://tu-frontend.vercel.app",
        "https://www.tudominio.com"  # si tienes dominio
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

---

# FASE 6: MONITOREO Y TESTING

## Paso 6.1: Configurar Monitoreo
```bash
# Sentry para error tracking (gratis hasta 5K errors/mes)
pip install sentry-sdk

# En src/app/main.py:
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="https://[tu-dsn]@sentry.io/[project-id]",
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
)
```

## Paso 6.2: Testing de Producción
```bash
# Script de testing automatizado
cat > test_production.py << 'EOF'
#!/usr/bin/env python3
import requests
import json

BASE_URL = "https://tu-backend.railway.app"

def test_health():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    print("✅ Health check OK")

def test_upload():
    # Test con archivo de prueba
    files = {"file": ("test.pdf", open("test.pdf", "rb"), "application/pdf")}
    response = requests.post(f"{BASE_URL}/api/v1/upload", files=files)
    assert response.status_code == 200
    print("✅ Upload test OK")

def test_methods():
    response = requests.get(f"{BASE_URL}/api/v1/upload-flexible/methods")
    assert response.status_code == 200
    data = response.json()
    assert "ocr_methods" in data
    print("✅ Methods endpoint OK")

if __name__ == "__main__":
    test_health()
    test_methods()
    # test_upload()  # Descomentar cuando tengas archivo de prueba
    print("🎉 Todos los tests pasaron!")
EOF
```

---

# FASE 7: OPTIMIZACIÓN Y ESCALADO

## Paso 7.1: Configurar CDN para Archivos
```bash
# Cloudflare R2 para storage de archivos
# 1. Ve a https://cloudflare.com/
# 2. R2 Object Storage → Create bucket: document-files
# 3. Configurar en .env:
R2_ENDPOINT=https://[account-id].r2.cloudflarestorage.com
R2_ACCESS_KEY_ID=[access-key]
R2_SECRET_ACCESS_KEY=[secret-key]
R2_BUCKET_NAME=document-files
```

## Paso 7.2: Configurar Backup Automático
```python
# Script de backup diario
import os
import subprocess
from datetime import datetime

def backup_database():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backup_{timestamp}.sql"
    
    # Backup de Supabase
    subprocess.run([
        "pg_dump", 
        os.getenv("DATABASE_URL"),
        "-f", backup_file
    ])
    
    # Subir a R2 o Google Drive
    print(f"Backup creado: {backup_file}")

# Configurar como cron job o GitHub Action
```

---

# 📊 RESUMEN DE URLS Y CREDENCIALES

## URLs de Producción:
- **Backend API**: `https://tu-proyecto.railway.app`
- **Frontend**: `https://tu-proyecto.vercel.app`  
- **Documentación**: `https://tu-proyecto.railway.app/docs`
- **Health Check**: `https://tu-proyecto.railway.app/health`

## Dashboards de Servicios:
- **Supabase**: https://app.supabase.com/project/[id]
- **Upstash**: https://console.upstash.com/
- **Railway**: https://railway.app/project/[id]
- **Vercel**: https://vercel.com/dashboard
- **OpenAI**: https://platform.openai.com/usage
- **Google Cloud**: https://console.cloud.google.com/

## Credenciales a Guardar Seguro:
```bash
# Archivo: production-credentials.txt (NO subir a Git)
Supabase DB URL: postgresql://postgres:[pass]@db.[id].supabase.co:5432/postgres
Upstash Redis URL: rediss://:[pass]@[host].upstash.io:6380
OpenAI API Key: sk-proj-[key]
Google Service Account: [archivo JSON]
Railway Project ID: [id]
Vercel Project ID: [id]
```

---

# 🚀 COMANDOS DE DEPLOY RÁPIDO

```bash
# Deploy completo en una línea (después de configurar servicios)
git add . && git commit -m "deploy: production ready" && git push origin main

# Verificar deploy
curl https://tu-proyecto.railway.app/health

# Ver logs en tiempo real
railway logs --follow  # (si instalas Railway CLI)
```

## Tiempo Total Estimado:
- ⏱️ **Configuración de servicios**: 20-30 minutos
- ⏱️ **Deploy backend**: 5-10 minutos  
- ⏱️ **Deploy frontend**: 3-5 minutos
- ⏱️ **Testing y optimización**: 10-15 minutos
- **🎯 TOTAL: 40-60 minutos**

## Costos Mensuales:
- **Primeros 6 meses**: $0 (todo en tier gratuito)
- **Después**: $10-30/mes (según uso)
- **Escalado**: $50-100/mes (para 10K+ documentos/mes)
