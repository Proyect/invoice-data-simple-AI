# ⚡ Deploy Rápido en 5 Pasos (30 minutos)

## 🚀 Paso 1: Preparación Automática (2 minutos)
```bash
# Ejecutar script de preparación
chmod +x deploy_automatico.sh
./deploy_automatico.sh

# Esto crea todos los archivos necesarios automáticamente
```

## 🔧 Paso 2: Configurar Servicios Cloud (15 minutos)

### A) Supabase (Base de Datos) - 3 minutos
1. Ve a https://supabase.com/ → Sign up with GitHub
2. New Project → Name: `document-extractor` → Create
3. Settings → Database → Copiar Connection string
4. SQL Editor → Ejecutar:
```sql
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
```

### B) Upstash (Redis) - 2 minutos
1. Ve a https://upstash.com/ → Sign up
2. Create Database → Redis → US-East-1 → Free
3. Copiar TLS URL

### C) OpenAI (LLM) - 3 minutos
1. Ve a https://platform.openai.com/ → Sign up
2. Verificar teléfono
3. API Keys → Create new → Copiar key

### D) Google Cloud Vision (OCR) - 7 minutos
1. Ve a https://console.cloud.google.com/ → Crear cuenta
2. New Project → Enable Vision API
3. IAM → Service Accounts → Create → Download JSON
4. Guardar como `google-service-account.json`

## 🚢 Paso 3: Deploy Backend en Railway (5 minutos)

### A) Configurar Railway
1. Ve a https://railway.app/ → Login with GitHub
2. New Project → Deploy from GitHub repo
3. Seleccionar tu repositorio

### B) Variables de Entorno
En Railway Dashboard → Variables, agregar:
```bash
APP_NAME=Document Extractor API - Production
DEBUG=False
DATABASE_URL=postgresql://postgres:[pass]@db.[proyecto].supabase.co:5432/postgres
REDIS_URL=rediss://:[pass]@[host].upstash.io:6380
OPENAI_API_KEY=sk-proj-[tu-key]
GOOGLE_APPLICATION_CREDENTIALS=/app/google-service-account.json
SECRET_KEY=[generar-32-caracteres-aleatorios]
```

### C) Subir Credenciales Google
- Variable: `GOOGLE_SERVICE_ACCOUNT_JSON`
- Value: [contenido completo del archivo JSON]

## 🌐 Paso 4: Deploy Frontend en Vercel (3 minutos)
```bash
# Solo si tienes frontend
cd frontend

# Configurar API URL
echo "REACT_APP_API_URL=https://tu-proyecto.railway.app/api/v1" > .env.production

# Deploy en Vercel
# 1. Ve a https://vercel.com/ → Import Git Repository
# 2. Root Directory: frontend
# 3. Deploy automático
```

## ✅ Paso 5: Verificar Deploy (5 minutos)
```bash
# Esperar 2-3 minutos a que termine el build en Railway
# Luego verificar:
python verify_deploy.py https://tu-proyecto.railway.app

# Debería mostrar:
# ✅ Health Check: OK (200)
# ✅ Root Endpoint: OK (200) 
# ✅ API Documentation: OK (200)
# ✅ Available Methods: OK (200)
```

---

# 🎯 URLs Finales

Después del deploy tendrás:
- **🔗 Backend API**: `https://tu-proyecto.railway.app`
- **📚 Documentación**: `https://tu-proyecto.railway.app/docs`
- **🌐 Frontend**: `https://tu-proyecto.vercel.app` (si aplica)
- **💾 Base de Datos**: Panel de Supabase
- **⚡ Cache**: Panel de Upstash

---

# 🆘 Solución de Problemas Comunes

## ❌ Error: "Build failed"
```bash
# Verificar logs en Railway Dashboard
# Común: falta variable de entorno
# Solución: Revisar que todas las variables estén configuradas
```

## ❌ Error: "Health check failed"
```bash
# Verificar que el puerto sea 8005
# Verificar que DATABASE_URL sea correcto
# Ver logs detallados en Railway
```

## ❌ Error: "Google Vision not working"
```bash
# Verificar que el JSON esté bien formateado
# Verificar que Vision API esté habilitada
# Verificar que el Service Account tenga permisos
```

---

# 💰 Costos Reales

## Primeros 6 meses: $0
- Supabase: 500MB gratis
- Upstash: 10k requests/día gratis  
- Railway: $5 USD/mes gratis
- Vercel: Ilimitado gratis
- OpenAI: $5 USD gratis
- Google Vision: $300 créditos + 1000/mes gratis

## Después de 6 meses: $10-30/mes
- Solo pagas por lo que excedas los límites gratuitos
- Escalado gradual según crecimiento

---

# 🎉 ¡Deploy Completado!

Tu aplicación estará funcionando en producción con:
- ✅ **Alta disponibilidad** (99.9% uptime)
- ✅ **Escalado automático** 
- ✅ **SSL/HTTPS** incluido
- ✅ **Monitoreo** integrado
- ✅ **Backup** automático (Supabase)
- ✅ **CDN global** (Vercel/Railway)

**Capacidad inicial**: 2,000-3,000 documentos/mes, 200-500 usuarios/mes















