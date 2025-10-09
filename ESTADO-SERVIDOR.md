# Estado del Servidor - Document Extractor API

**Fecha**: 9 de octubre de 2025  
**Puerto**: 8005  
**Estado**: ✅ FUNCIONANDO

---

## ✅ Servicios Funcionando

### 1. API Principal
- **URL**: http://localhost:8005
- **Status**: ✅ ACTIVO
- **Documentación**: http://localhost:8005/docs
- **Health Check**: http://localhost:8005/health

### 2. Base de Datos PostgreSQL
- **Estado**: ✅ CONECTADA
- **Puerto**: 5434 (Docker)
- **Tabla**: `documents` creada con JSONB
- **Índices**: 10 índices optimizados (incluyendo GIN)

### 3. Endpoints Disponibles

| Endpoint | Método | Estado | Descripción |
|----------|--------|--------|-------------|
| `/` | GET | ✅ | Información de la API |
| `/health` | GET | ✅ | Health check |
| `/docs` | GET | ✅ | Documentación Swagger |
| `/api/v1/upload` | POST | ⚠️ | Upload simple (requiere Tesseract) |
| `/api/v1/upload-flexible` | POST | ⚠️ | Upload flexible (requiere Tesseract) |
| `/api/v1/upload/test` | GET | ⚠️ | Test OCR (requiere Tesseract) |
| `/api/v1/documents` | GET | ✅ | Listar documentos |
| `/api/v1/upload-flexible/methods` | GET | ✅ | Ver métodos disponibles |

---

## ⚠️ Requiere Configuración

### 1. Tesseract OCR (Para desarrollo local)

**Estado**: ❌ No instalado  
**Necesario para**: Extraer texto de imágenes/PDFs

**Instalación**:
1. Descargar: https://github.com/UB-Mannheim/tesseract/wiki
2. Instalar en: `C:\Program Files\Tesseract-OCR`
3. Agregar a `.env`:
   ```env
   TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
   ```

**Alternativa**: Usar Docker (Tesseract ya incluido)
```bash
docker-compose up -d app
# API en http://localhost:8006
```

### 2. APIs Externas (Opcionales)

#### OpenAI GPT
- **Estado**: ❌ No configurado
- **Uso**: Extracción inteligente con LLM
- **Configurar**: 
  ```env
  OPENAI_API_KEY=sk-...
  ```

#### Google Cloud Vision
- **Estado**: ❌ No configurado
- **Uso**: OCR de alta precisión
- **Configurar**: 
  ```env
  GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
  ```

#### AWS Textract
- **Estado**: ❌ No configurado
- **Uso**: OCR especializado en formularios
- **Configurar**:
  ```env
  AWS_ACCESS_KEY_ID=...
  AWS_SECRET_ACCESS_KEY=...
  ```

---

## 🧪 Pruebas Realizadas

### Health Check ✅
```json
{
  "status": "healthy",
  "port": 8005,
  "database": "PostgreSQL",
  "cache": "Redis",
  "processing": "Async"
}
```

### API Info ✅
```json
{
  "message": "Document Extractor API - Flexible Mode",
  "version": "2.1.0",
  "status": "Funcionando",
  "features": [
    "Múltiples métodos de OCR",
    "Múltiples métodos de extracción",
    "Base de datos PostgreSQL/SQLite",
    "Procesamiento flexible"
  ]
}
```

### Test OCR ⚠️
```json
{
  "error": "tesseract is not installed",
  "tesseract_installed": false,
  "message": "Instala Tesseract OCR"
}
```

---

## 📊 Opciones de Uso

### Opción A: Desarrollo Local (Actual)

**Estado**: ✅ API funcionando, ⚠️ OCR no disponible

**Pros**:
- API completamente funcional
- Base de datos PostgreSQL funcionando
- Fácil de debuggear

**Contras**:
- Requiere instalar Tesseract manualmente
- No puede procesar documentos aún

**Para activar OCR**:
```bash
# 1. Instalar Tesseract
# 2. Configurar .env
# 3. Reiniciar servidor
```

---

### Opción B: Docker (Recomendado)

**Estado**: ✅ Todo incluido

**Pros**:
- Tesseract preinstalado
- PostgreSQL incluido
- Redis incluido
- No requiere configuración

**Iniciar**:
```bash
docker-compose up -d
# API en http://localhost:8006/docs
```

---

## 🚀 Cómo Acceder

### Navegador
```
Documentación interactiva:
http://localhost:8005/docs

Redoc:
http://localhost:8005/redoc

Info:
http://localhost:8005/
```

### PowerShell
```powershell
# Health check
Invoke-WebRequest -Uri http://localhost:8005/health

# Info
Invoke-WebRequest -Uri http://localhost:8005/
```

### Python
```python
import requests

# Health check
response = requests.get("http://localhost:8005/health")
print(response.json())

# Upload (cuando Tesseract esté instalado)
files = {"file": open("documento.pdf", "rb")}
data = {"document_type": "factura"}
response = requests.post(
    "http://localhost:8005/api/v1/upload",
    files=files,
    data=data
)
print(response.json())
```

---

## 🔧 Comandos Útiles

### Ver Logs
```bash
# Si está en background, ver proceso
Get-Process | Where-Object {$_.Path -like "*python*"}

# Reiniciar servidor
# Ctrl+C en terminal donde corre
# O matar proceso y volver a iniciar
```

### Detener Servidor
```bash
# Encontrar PID
netstat -ano | findstr :8005

# Matar proceso
taskkill /F /PID <PID>
```

### Reiniciar
```bash
.venv\Scripts\activate
python start.py
```

---

## 📝 Próximos Pasos

### Para Desarrollo Local
1. ✅ Servidor funcionando
2. ✅ PostgreSQL conectado
3. ⏳ Instalar Tesseract OCR
4. ⏳ Configurar OpenAI (opcional)
5. ⏳ Probar upload de documentos

### Para Producción
1. ✅ Migrar a Docker
2. ⏳ Configurar APIs cloud
3. ⏳ Configurar variables de entorno
4. ⏳ Habilitar HTTPS

---

## ✅ Resumen

```
┌─────────────────────────────────────────┐
│    SERVIDOR FUNCIONANDO CORRECTAMENTE   │
├─────────────────────────────────────────┤
│ ✅ API: http://localhost:8005          │
│ ✅ PostgreSQL: Conectada y funcionando │
│ ✅ Migraciones: Aplicadas              │
│ ✅ Documentación: /docs                │
│ ⚠️  Tesseract: Requiere instalación    │
└─────────────────────────────────────────┘
```

**Próxima acción recomendada**:
1. Ir a http://localhost:8005/docs para explorar la API
2. Instalar Tesseract para habilitar OCR
3. O usar Docker: `docker-compose up -d`

---

**Servidor iniciado por**: Usuario  
**Fecha**: 9 de octubre de 2025  
**Versión**: 2.1.0  
**Estado**: 🟢 ACTIVO

