# 🆓 Stack Completamente Gratuito para Document Extractor

## Arquitectura Recomendada

```
Frontend (React) → Vercel (Gratis)
     ↓
Backend (FastAPI) → Railway (Gratis $5/mes)
     ↓
Database → Supabase PostgreSQL (Gratis 500MB)
     ↓
Cache → Upstash Redis (Gratis 10k req/día)
     ↓
Storage → Cloudflare R2 (Gratis 10GB)
     ↓
AI APIs → OpenAI + Google Vision (Créditos gratis)
```

## Configuración por Servicio

### 1. Supabase (Base de Datos)
```bash
# Registro: https://supabase.com/
# Crear proyecto → Settings → Database → Connection string
DATABASE_URL=postgresql://postgres:[password]@db.[proyecto].supabase.co:5432/postgres
```

### 2. Upstash (Redis Cache)
```bash
# Registro: https://upstash.com/
# Create Database → Copy REST URL
REDIS_URL=rediss://:[password]@[host].upstash.io:6380
```

### 3. Railway (Deploy Backend)
```bash
# Registro: https://railway.app/
# Connect GitHub → Deploy from repo
# Variables de entorno se configuran en el dashboard
```

### 4. Vercel (Deploy Frontend)
```bash
# Registro: https://vercel.com/
# Import Git Repository → Auto-deploy
npm run build  # Se ejecuta automáticamente
```

### 5. Cloudflare R2 (File Storage)
```bash
# Registro: https://cloudflare.com/
# R2 Object Storage → Create bucket
# API tokens para acceso programático
```

### 6. OpenAI (LLM)
```bash
# Registro: https://platform.openai.com/
# $5 USD gratis para nuevas cuentas
OPENAI_API_KEY=sk-proj-[tu-key]
```

### 7. Google Cloud Vision (OCR)
```bash
# Registro: https://console.cloud.google.com/
# $300 USD créditos + 1000 requests/mes gratis permanente
# Enable Vision API → Create Service Account
GOOGLE_APPLICATION_CREDENTIALS=./service-account.json
```

## Límites y Capacidades

| Servicio | Límite Gratuito | Renovación |
|----------|----------------|------------|
| **Supabase** | 500MB DB + 2GB bandwidth | Mensual |
| **Upstash** | 10k requests + 256MB | Diario |
| **Railway** | $5 USD compute | Mensual |
| **Vercel** | 100GB bandwidth | Mensual |
| **Cloudflare R2** | 10GB + 1M requests | Mensual |
| **OpenAI** | $5 USD (~2500 requests) | Una vez |
| **Google Vision** | 1000 requests | Mensual |

## Estimación de Capacidad

Con estos límites gratuitos puedes manejar aproximadamente:
- **📄 2,000-5,000 documentos/mes** (dependiendo del tamaño)
- **👥 100-500 usuarios activos/mes**
- **🔄 10,000 requests de cache/día**
- **📊 500MB de datos estructurados**
- **📁 10GB de archivos subidos**

## Comandos de Deploy

### Backend a Railway:
```bash
# 1. Conectar repo a Railway
# 2. Configurar variables de entorno
# 3. Deploy automático en cada push
git push origin main
```

### Frontend a Vercel:
```bash
# 1. Conectar repo a Vercel
# 2. Configurar build command: npm run build
# 3. Deploy automático
git push origin main
```

## Monitoreo Gratuito

### Sentry (Error Tracking)
```bash
# 5,000 errors/mes gratis
pip install sentry-sdk
# Configurar en main.py
```

### Uptime Robot (Monitoring)
```bash
# 50 monitors gratis
# Ping cada 5 minutos
# Alertas por email/SMS
```

## Escalabilidad

Cuando superes los límites gratuitos:
1. **Supabase Pro**: $25/mes (8GB DB)
2. **Upstash Pro**: $10/mes (100k requests/día)
3. **Railway Pro**: $20/mes (más compute)
4. **OpenAI Pay-as-go**: $0.002/request
5. **Google Vision**: $1.50/1000 imágenes

## Alternativas por Región

### Europa (GDPR Compliant):
- **Database**: Supabase EU
- **Deploy**: Railway EU / Render EU
- **Storage**: Cloudflare R2 (global)

### Asia-Pacífico:
- **Database**: PlanetScale (global)
- **Deploy**: Vercel (edge global)
- **Cache**: Upstash (multi-region)












