# Configuración de Puertos en Docker 🐳

## 📋 Puertos Configurados

### **Puertos Externos (Tu PC)**

Estos son los puertos que usarás para acceder desde tu navegador o terminal:

| Servicio | Puerto Externo | Descripción |
|----------|----------------|-------------|
| **FastAPI** | **8006** | API principal |
| **PostgreSQL** | **5433** | Base de datos |
| **Redis** | **6380** | Cache y colas |
| **PgAdmin** | **5050** | Administrador de DB |

### **Puertos Internos (Docker)**

Estos son los puertos que usan los contenedores entre sí:

| Servicio | Puerto Interno |
|----------|----------------|
| FastAPI | 8005 |
| PostgreSQL | 5432 |
| Redis | 6379 |
| PgAdmin | 80 |

## 🌐 URLs de Acceso

### **Aplicación Principal**
```
API Base:          http://localhost:8006
Documentación:     http://localhost:8006/docs
Health Check:      http://localhost:8006/health
Test OCR:          http://localhost:8006/api/v1/upload/test
Upload Document:   http://localhost:8006/api/v1/upload
List Documents:    http://localhost:8006/api/v1/documents
```

### **Base de Datos**
```
PgAdmin Web:       http://localhost:5050
  - Email:         admin@admin.com
  - Password:      admin

PostgreSQL:        localhost:5433
  - Usuario:       postgres
  - Password:      postgres
  - Base de datos: document_extractor
```

### **Cache**
```
Redis:             localhost:6380
```

## 🔄 Cambiar Puertos (Si es Necesario)

Si algún puerto sigue estando ocupado, edita `docker-compose.yml`:

```yaml
services:
  app:
    ports:
      - "8007:8005"  # Cambiar 8006 por 8007

  postgres:
    ports:
      - "5434:5432"  # Cambiar 5433 por 5434

  redis:
    ports:
      - "6381:6379"  # Cambiar 6380 por 6381
```

Luego ejecuta:
```bash
docker-compose down
docker-compose up -d
```

## 🧪 Verificar Puertos

### **Verificar que los Puertos Están Libres**

```powershell
# Ver qué puertos están en uso
netstat -ano | findstr "8006 5433 6380 5050"
```

### **Verificar que Docker Está Usando los Puertos**

```bash
docker-compose ps
```

Deberías ver:
```
NAME                    PORTS
app-1                  0.0.0.0:8006->8005/tcp
postgres-1             0.0.0.0:5433->5432/tcp
redis-1                0.0.0.0:6380->6379/tcp
pgadmin-1              0.0.0.0:5050->80/tcp
```

## 📊 Mapeo de Puertos Explicado

```
Tu PC (Windows)         Docker Container
─────────────          ─────────────────

localhost:8006   ───►  app:8005 (FastAPI)
localhost:5433   ───►  postgres:5432 (PostgreSQL)
localhost:6380   ───►  redis:6379 (Redis)
localhost:5050   ───►  pgadmin:80 (PgAdmin)
```

**Ventaja**: Los puertos externos no conflictúan con servicios que ya estén corriendo en tu PC.

## 🎯 Ejemplos de Uso con Nuevos Puertos

### **1. Health Check**
```bash
curl http://localhost:8006/health
```

### **2. Subir Documento**
```bash
curl -X POST "http://localhost:8006/api/v1/upload" \
  -F "file=@factura.pdf" \
  -F "document_type=factura"
```

### **3. Listar Documentos**
```bash
curl http://localhost:8006/api/v1/documents
```

### **4. Ver Documentación**
```
http://localhost:8006/docs
```

### **5. Conectar a PostgreSQL**
```bash
psql -h localhost -p 5433 -U postgres -d document_extractor
```

### **6. Conectar a Redis**
```bash
redis-cli -h localhost -p 6380
```

## 🔒 Configuración de Seguridad (Opcional)

Para producción, cambia las contraseñas en `docker-compose.yml`:

```yaml
postgres:
  environment:
    - POSTGRES_PASSWORD=tu_contraseña_segura

pgadmin:
  environment:
    - PGADMIN_DEFAULT_PASSWORD=tu_contraseña_segura
```

## 📞 Soporte

Si tienes problemas con los puertos:

1. **Verificar qué puertos están ocupados**:
   ```bash
   netstat -ano | findstr "8006"
   ```

2. **Cambiar puerto si es necesario**:
   - Edita `docker-compose.yml`
   - Cambia `"8006:8005"` por `"8007:8005"`
   - Reinicia: `docker-compose down && docker-compose up -d`

---

**Configuración Actual**:
- API: Puerto 8006
- PostgreSQL: Puerto 5433
- Redis: Puerto 6380
- PgAdmin: Puerto 5050

¡Todos los puertos configurados para evitar conflictos! ✅


