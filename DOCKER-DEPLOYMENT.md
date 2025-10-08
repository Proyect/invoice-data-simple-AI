# Implementación en Docker - Guía Completa 🐳

## 🎯 Puertos Configurados (Sin Conflictos)

| Servicio | Puerto Externo | Puerto Interno | Acceso |
|----------|----------------|----------------|---------|
| **API (FastAPI)** | **8006** | 8005 | http://localhost:8006 |
| **PostgreSQL** | **5433** | 5432 | localhost:5433 |
| **Redis** | **6380** | 6379 | localhost:6380 |
| **PgAdmin** | **5050** | 80 | http://localhost:5050 |

**Nota**: Los puertos externos fueron cambiados para evitar conflictos con servicios existentes.

## 🚀 Instalación en Docker (Paso a Paso)

### **Paso 1: Verificar Docker**

```bash
docker --version
docker-compose --version
```

Deberías ver:
```
Docker version 28.x.x
Docker Compose version v2.x.x
```

### **Paso 2: Detener Aplicación Local**

```bash
# Detener Python local
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
```

### **Paso 3: Construir Imágenes Docker**

```bash
# Esto puede tardar 5-10 minutos la primera vez
docker-compose build
```

Durante la construcción se instalará automáticamente:
- ✅ Python 3.11
- ✅ **Tesseract OCR** (con idioma español)
- ✅ **Poppler** (para PDFs)
- ✅ **spaCy** modelo español
- ✅ Todas las dependencias de Python

### **Paso 4: Iniciar Servicios**

```bash
docker-compose up -d
```

Esto iniciará:
- ✅ API (FastAPI)
- ✅ PostgreSQL
- ✅ Redis
- ✅ Worker (procesamiento asíncrono)

### **Paso 5: Verificar que Todo Funciona**

```bash
# Esperar 30 segundos para que todo inicie
Start-Sleep -Seconds 30

# Verificar salud de la aplicación
curl http://localhost:8006/health
```

## 📊 URLs de Acceso

### **Aplicación Principal**
- **API**: http://localhost:8006
- **Documentación**: http://localhost:8006/docs
- **Health Check**: http://localhost:8006/health
- **Info del Sistema**: http://localhost:8006/info

### **Base de Datos**
- **PgAdmin**: http://localhost:5050
  - Email: `admin@admin.com`
  - Password: `admin`
- **PostgreSQL**: `localhost:5433`
  - Usuario: `postgres`
  - Password: `postgres`
  - Base de datos: `document_extractor`

### **Redis**
- **Puerto**: `localhost:6380`

## 🧪 Probar la Aplicación en Docker

### **1. Verificar Estado de Servicios**

```bash
docker-compose ps
```

Deberías ver algo como:
```
NAME                              STATUS
invoice-data-simple-ai-app-1      Up
invoice-data-simple-ai-postgres-1 Up
invoice-data-simple-ai-redis-1    Up
invoice-data-simple-ai-worker-1   Up
```

### **2. Verificar Health Check**

```bash
# PowerShell
Invoke-RestMethod -Uri "http://localhost:8006/health"
```

Respuesta esperada:
```json
{
  "status": "healthy",
  "port": 8005,
  "database": "PostgreSQL",
  "cache": "Redis",
  "processing": "Async"
}
```

### **3. Verificar Tesseract Funciona**

```bash
curl http://localhost:8006/api/v1/upload/test
```

Respuesta esperada:
```json
{
  "tesseract_version": "5.x.x",
  "spacy_loaded": true,
  "status": "OK",
  "upload_dir": "uploads",
  "upload_dir_exists": true
}
```

### **4. Subir una Factura**

**Opción A: Interfaz Web**
```
1. Abre: http://localhost:8006/docs
2. POST /api/v1/upload
3. Try it out
4. Sube tu factura
5. Execute
6. ¡Ve los datos extraídos!
```

**Opción B: cURL**
```bash
curl -X POST "http://localhost:8006/api/v1/upload" \
  -F "file=@C:/ruta/a/factura.pdf" \
  -F "document_type=factura"
```

**Opción C: PowerShell**
```powershell
$file = "C:\Users\amdiaz\Desktop\code\Python\v.13.13\invoice-data-simple-AI\uploads\20251007_155000_test_invoice.jpg"

$form = @{
    file = Get-Item $file
    document_type = "factura"
}

$response = Invoke-WebRequest -Uri "http://localhost:8006/api/v1/upload" -Method POST -Form $form
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

## 🔧 Comandos Útiles de Docker

### **Gestión de Contenedores**

```bash
# Ver servicios corriendo
docker-compose ps

# Ver logs de la aplicación
docker-compose logs -f app

# Ver logs del worker
docker-compose logs -f worker

# Ver logs de todos los servicios
docker-compose logs -f

# Reiniciar solo la aplicación
docker-compose restart app

# Detener todos los servicios
docker-compose down

# Detener y eliminar volúmenes (limpiar todo)
docker-compose down -v
```

### **Acceder a Contenedores**

```bash
# Shell en el contenedor de la app
docker-compose exec app /bin/bash

# Conectar a PostgreSQL
docker-compose exec postgres psql -U postgres -d document_extractor

# Conectar a Redis
docker-compose exec redis redis-cli
```

### **Monitoreo**

```bash
# Ver uso de recursos
docker stats

# Ver estado de servicios
docker-compose ps

# Ver logs en tiempo real
docker-compose logs -f app
```

## 📁 Estructura de Volúmenes

Los siguientes directorios están montados como volúmenes:

```
./src         →  /app/src         (código fuente)
./uploads     →  /app/uploads     (archivos subidos)
./outputs     →  /app/outputs     (resultados)
./data        →  /app/data        (base de datos SQLite)
./logs        →  /app/logs        (logs de la aplicación)
```

**Ventaja**: Los cambios en estos directorios se reflejan inmediatamente en Docker.

## 🗄️ Conectar a PostgreSQL

### **Desde PgAdmin (Interfaz Web)**

1. Abre: http://localhost:5050
2. Login:
   - Email: `admin@admin.com`
   - Password: `admin`
3. Add New Server:
   - Name: `Document Extractor`
   - Host: `postgres`
   - Port: `5432`
   - Database: `document_extractor`
   - Username: `postgres`
   - Password: `postgres`

### **Desde Cliente Externo**

```bash
# Connection string
postgresql://postgres:postgres@localhost:5433/document_extractor

# Con psql
psql -h localhost -p 5433 -U postgres -d document_extractor
```

## 🔄 Desarrollo con Docker

### **Hot Reload Activo**

Los cambios en el código se reflejan automáticamente:

1. Edita archivo en `src/app/`
2. Guarda
3. Docker detecta cambio y recarga automáticamente
4. Actualiza navegador para ver cambios

### **Ver Logs en Tiempo Real**

```bash
docker-compose logs -f app
```

## 🚨 Troubleshooting

### **Error: Puerto ya en uso**

```bash
# Ver qué proceso usa el puerto
netstat -ano | findstr :8006

# Cambiar puerto en docker-compose.yml
ports:
  - "8007:8005"  # Usar 8007 en lugar de 8006
```

### **Error: Contenedor no inicia**

```bash
# Ver logs del contenedor
docker-compose logs app

# Ver logs del worker
docker-compose logs worker
```

### **Error: Base de datos no conecta**

```bash
# Verificar PostgreSQL
docker-compose logs postgres

# Verificar que está corriendo
docker-compose ps postgres
```

### **Error: "No module named..."**

```bash
# Reconstruir imagen
docker-compose build --no-cache app

# Reiniciar
docker-compose up -d
```

## 🧹 Limpiar y Reiniciar

### **Reinicio Limpio**

```bash
# Detener todo
docker-compose down

# Eliminar volúmenes (CUIDADO: borra datos)
docker-compose down -v

# Reconstruir
docker-compose build

# Iniciar de nuevo
docker-compose up -d
```

### **Limpiar Docker Completamente**

```bash
# Detener contenedores
docker-compose down -v

# Limpiar imágenes no usadas
docker image prune -a

# Limpiar todo Docker
docker system prune -a --volumes
```

## 📊 Migración de Datos

### **Exportar Datos de SQLite a PostgreSQL**

```bash
# 1. Conectar a PostgreSQL en Docker
docker-compose exec app python

# 2. En Python shell:
import sqlite3
import psycopg2
import json

# Conectar a SQLite
sqlite_conn = sqlite3.connect('./data/documents.db')
sqlite_cursor = sqlite_conn.cursor()

# Conectar a PostgreSQL
pg_conn = psycopg2.connect(
    host="postgres",
    port=5432,
    database="document_extractor",
    user="postgres",
    password="postgres"
)
pg_cursor = pg_conn.cursor()

# Migrar datos...
```

## 🎯 Endpoints con Nuevos Puertos

| Endpoint | URL | Descripción |
|----------|-----|-------------|
| **Raíz** | http://localhost:8006/ | Info de la API |
| **Docs** | http://localhost:8006/docs | Documentación interactiva |
| **Health** | http://localhost:8006/health | Estado de salud |
| **Upload** | http://localhost:8006/api/v1/upload | Subir documento |
| **Documents** | http://localhost:8006/api/v1/documents | Listar documentos |
| **Stats** | http://localhost:8006/api/v1/documents/stats | Estadísticas |

## 🎉 Ventajas de Docker

✅ **Tesseract preinstalado** - No necesitas instalarlo manualmente
✅ **Poppler preinstalado** - PDFs funcionan automáticamente
✅ **PostgreSQL incluido** - Base de datos robusta
✅ **Redis incluido** - Cache y procesamiento asíncrono
✅ **Worker automático** - Procesamiento en background
✅ **Entorno consistente** - Funciona igual en cualquier máquina
✅ **Fácil despliegue** - Un comando para todo

## 📝 Comandos de Referencia Rápida

```bash
# Construir
docker-compose build

# Iniciar
docker-compose up -d

# Ver logs
docker-compose logs -f app

# Estado
docker-compose ps

# Detener
docker-compose down

# Health check
curl http://localhost:8006/health

# Documentación
# Abrir: http://localhost:8006/docs
```

## 🎯 Próximos Pasos

1. **Construir imágenes**: `docker-compose build`
2. **Iniciar servicios**: `docker-compose up -d`
3. **Verificar**: `curl http://localhost:8006/health`
4. **Probar**: http://localhost:8006/docs
5. **Subir factura**: POST /api/v1/upload

---

**¡Con Docker todo está listo para funcionar sin instalar nada más!** 🚀


