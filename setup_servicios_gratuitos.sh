#!/bin/bash

# Script para configurar servicios gratuitos automáticamente
echo "🚀 Configurando servicios gratuitos para Document Extractor..."

# Crear archivo .env con plantilla
cat > .env << 'EOF'
# ===========================================
# SERVICIOS GRATUITOS EN LA NUBE
# ===========================================

# Aplicación
APP_NAME=Document Extractor API - Cloud Gratuito
DEBUG=True
HOST=0.0.0.0
PORT=8005

# Supabase PostgreSQL (500MB gratis)
# 1. Registrarse en https://supabase.com/
# 2. Crear proyecto
# 3. Copiar connection string
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROYECTO].supabase.co:5432/postgres

# Upstash Redis (10k requests/día gratis)
# 1. Registrarse en https://upstash.com/
# 2. Crear database
# 3. Copiar TLS URL
REDIS_URL=rediss://:[PASSWORD]@[HOST].upstash.io:6380
REDIS_HOST=[HOST].upstash.io
REDIS_PORT=6380

# OpenAI ($5 USD gratis para nuevas cuentas)
# 1. Registrarse en https://platform.openai.com/
# 2. Crear API key
OPENAI_API_KEY=sk-proj-[TU_KEY]
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=500

# Google Cloud Vision ($300 créditos + 1000/mes gratis)
# 1. Registrarse en https://console.cloud.google.com/
# 2. Habilitar Vision API
# 3. Crear Service Account
GOOGLE_APPLICATION_CREDENTIALS=./google-service-account.json
GOOGLE_VISION_DAILY_LIMIT=50

# Cloudflare R2 (10GB gratis)
# 1. Registrarse en https://cloudflare.com/
# 2. Crear R2 bucket
# 3. Generar API tokens
# R2_ENDPOINT=https://[account].r2.cloudflarestorage.com
# R2_ACCESS_KEY=[ACCESS_KEY]
# R2_SECRET_KEY=[SECRET_KEY]

# Configuración básica
SECRET_KEY=$(openssl rand -hex 32)
UPLOAD_DIR=uploads
OUTPUT_DIR=outputs
TESSERACT_CONFIDENCE_THRESHOLD=0.7
EOF

echo "✅ Archivo .env creado con plantilla"

# Crear directorio para credenciales
mkdir -p credentials

# Crear script de verificación
cat > verificar_servicios.py << 'EOF'
#!/usr/bin/env python3
"""
Script para verificar que todos los servicios gratuitos están configurados
"""
import os
from dotenv import load_dotenv

load_dotenv()

def check_service(name, env_var, required=True):
    value = os.getenv(env_var)
    status = "✅" if value and value != f"[{env_var}]" else "❌"
    required_text = " (REQUERIDO)" if required else " (OPCIONAL)"
    print(f"{status} {name}: {env_var}{required_text}")
    return bool(value and value != f"[{env_var}]")

print("🔍 Verificando configuración de servicios gratuitos...\n")

# Servicios básicos
db_ok = check_service("Supabase PostgreSQL", "DATABASE_URL")
redis_ok = check_service("Upstash Redis", "REDIS_URL", False)

# APIs de IA
openai_ok = check_service("OpenAI API", "OPENAI_API_KEY", False)
google_ok = check_service("Google Vision", "GOOGLE_APPLICATION_CREDENTIALS", False)

# Verificar archivos
google_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if google_file and os.path.exists(google_file):
    print("✅ Google Service Account file encontrado")
else:
    print("❌ Google Service Account file no encontrado")

print(f"\n📊 Resumen:")
print(f"   Base de datos: {'✅' if db_ok else '❌'}")
print(f"   Cache: {'✅' if redis_ok else '⚠️  Opcional'}")
print(f"   IA/ML: {'✅' if (openai_ok or google_ok) else '⚠️  Opcional'}")

if db_ok:
    print("\n🚀 ¡Configuración mínima lista! Puedes ejecutar la aplicación.")
else:
    print("\n⚠️  Necesitas configurar al menos la base de datos para continuar.")

print("\n📚 Guías de configuración:")
print("   Supabase: https://supabase.com/docs/guides/getting-started")
print("   Upstash: https://docs.upstash.com/redis")
print("   OpenAI: https://platform.openai.com/docs/quickstart")
print("   Google Cloud: https://cloud.google.com/vision/docs/setup")
EOF

chmod +x verificar_servicios.py

echo "✅ Script de verificación creado: ./verificar_servicios.py"

# Crear README con instrucciones
cat > SERVICIOS_GRATUITOS.md << 'EOF'
# 🆓 Guía de Servicios Gratuitos

## Pasos de Configuración

### 1. Supabase (Base de Datos) - REQUERIDO
```bash
# 1. Ve a https://supabase.com/
# 2. Crea cuenta gratuita
# 3. Nuevo proyecto
# 4. Settings → Database → Connection string
# 5. Copia y pega en DATABASE_URL del .env
```

### 2. Upstash (Redis Cache) - OPCIONAL
```bash
# 1. Ve a https://upstash.com/
# 2. Crea cuenta gratuita  
# 3. Create Database → Redis
# 4. Copia TLS URL y pega en REDIS_URL del .env
```

### 3. OpenAI (IA) - OPCIONAL
```bash
# 1. Ve a https://platform.openai.com/
# 2. Crea cuenta (verificar teléfono)
# 3. API Keys → Create new key
# 4. Copia y pega en OPENAI_API_KEY del .env
```

### 4. Google Cloud Vision (OCR) - OPCIONAL
```bash
# 1. Ve a https://console.cloud.google.com/
# 2. Crea proyecto nuevo
# 3. APIs & Services → Enable Vision API
# 4. Credentials → Create Service Account
# 5. Descarga JSON y guarda como google-service-account.json
```

## Verificar Configuración
```bash
python verificar_servicios.py
```

## Ejecutar Aplicación
```bash
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn src.app.main:app --reload --port 8005
```

## URLs de Prueba
- API: http://localhost:8005/docs
- Health: http://localhost:8005/health
- Métodos: http://localhost:8005/api/v1/upload-flexible/methods
EOF

echo "✅ Documentación creada: ./SERVICIOS_GRATUITOS.md"

echo ""
echo "🎉 ¡Configuración completada!"
echo ""
echo "📋 Próximos pasos:"
echo "   1. Edita el archivo .env con tus credenciales"
echo "   2. Ejecuta: python verificar_servicios.py"
echo "   3. Lee: ./SERVICIOS_GRATUITOS.md"
echo ""
echo "🔗 Enlaces útiles:"
echo "   • Supabase: https://supabase.com/"
echo "   • Upstash: https://upstash.com/"
echo "   • OpenAI: https://platform.openai.com/"
echo "   • Google Cloud: https://console.cloud.google.com/"

























