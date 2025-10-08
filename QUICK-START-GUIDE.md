# Guía de Inicio Rápido: Local → Docker 🚀

Guía paso a paso para empezar con desarrollo local y luego migrar a Docker.

## 🎯 Estrategia Recomendada

1. **Desarrollo Local** - Para desarrollo rápido e iterativo
2. **Migración a Docker** - Para producción y despliegue

## 🐍 Paso 1: Desarrollo Local

### **Configuración Inicial**

```bash
# Opción 1: Script automático
chmod +x quick-start-venv.sh
./quick-start-venv.sh

# Opción 2: Comandos manuales
make setup-venv
make dev-venv
```

### **Verificar que Funciona**

```bash
# Abrir en navegador
http://localhost:8005/docs

# O probar con curl
curl http://localhost:8005/health
```

### **Desarrollar y Probar**

```bash
# Hacer cambios en el código
# Probar funcionalidad
# Ejecutar tests
make test

# Formatear código
make format
```

## 🐳 Paso 2: Migración a Docker

### **Cuando Estés Listo**

- ✅ Funcionalidad básica completada
- ✅ Tests pasando
- ✅ Código estable

### **Migrar Automáticamente**

```bash
# Script de migración
chmod +x migrate-to-docker.sh
./migrate-to-docker.sh

# O usando make
make migrate-to-docker
```

### **Verificar Migración**

```bash
# Verificar servicios
docker-compose ps

# Verificar aplicación
curl http://localhost:8005/health

# Ver logs
docker-compose logs -f app
```

## 🔄 Comandos Útiles

### **Desarrollo Local**

```bash
# Configurar
make setup-venv

# Iniciar
make dev-venv

# Shell en venv
make venv-shell

# Tests
make test

# Formatear
make format
```

### **Docker**

```bash
# Configurar
make setup

# Desarrollo
make dev

# Producción
make prod

# Logs
make logs

# Shell en contenedor
make shell
```

### **Migración**

```bash
# Local → Docker
make migrate-to-docker

# Docker → Local
make back-to-local
```

## 📋 Checklist de Desarrollo

### **Durante Desarrollo Local**

- [ ] **Código funciona** - Sin errores críticos
- [ ] **Tests pasan** - `make test` exitoso
- [ ] **API responde** - Endpoints funcionando
- [ ] **Logs limpios** - Sin errores en consola

### **Antes de Migrar a Docker**

- [ ] **Funcionalidad completa** - Todas las features implementadas
- [ ] **Tests pasando** - Cobertura adecuada
- [ ] **Documentación actualizada** - README y comentarios
- [ ] **Variables de entorno** - `.env` configurado

### **Después de Migrar a Docker**

- [ ] **Contenedores funcionando** - `docker-compose ps`
- [ ] **Base de datos conectada** - PostgreSQL/Redis OK
- [ ] **API respondiendo** - Health check OK
- [ ] **Performance aceptable** - Tiempos de respuesta OK

## 🚨 Troubleshooting

### **Problemas en Desarrollo Local**

#### **Error: Módulo no encontrado**
```bash
# Verificar entorno virtual activado
which python

# Reinstalar dependencias
pip install -r requirements-venv.txt
```

#### **Error: Tesseract no encontrado**
```bash
# Instalar Tesseract
# Ubuntu: sudo apt install tesseract-ocr
# macOS: brew install tesseract
# Windows: Descargar desde GitHub

# Configurar en .env
TESSERACT_CMD=/usr/bin/tesseract
```

#### **Error: Puerto ocupado**
```bash
# Verificar qué usa el puerto
lsof -i :8005

# Cambiar puerto en .env
PORT=8006
```

### **Problemas en Docker**

#### **Error: Imagen no construye**
```bash
# Limpiar Docker
docker system prune -f

# Reconstruir
docker-compose build --no-cache
```

#### **Error: Base de datos no conecta**
```bash
# Verificar PostgreSQL
docker-compose logs postgres

# Verificar variables
docker-compose exec app env | grep DATABASE
```

#### **Error: Redis no disponible**
```bash
# Verificar Redis
docker-compose logs redis

# Probar conexión
docker-compose exec app redis-cli ping
```

## 📊 Comparación de Ambientes

| Aspecto | Desarrollo Local | Docker |
|---------|------------------|---------|
| **Velocidad de inicio** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Debug** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Consistencia** | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Recursos** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Producción** | ⭐⭐ | ⭐⭐⭐⭐⭐ |

## 🎯 Flujo de Trabajo Típico

### **Día 1-3: Desarrollo Local**
```bash
# Configurar
make setup-venv

# Desarrollar
make dev-venv

# Hacer cambios
# Probar funcionalidad
# Ejecutar tests
make test
```

### **Día 4: Migración a Docker**
```bash
# Migrar
make migrate-to-docker

# Verificar
make health
make stats

# Probar en Docker
curl http://localhost:8005/api/v1/upload-optimized -F "file=@test.pdf"
```

### **Día 5: Producción**
```bash
# Modo producción
make prod

# Monitorear
make logs
make stats
```

## 🚀 URLs Importantes

### **Desarrollo Local**
- **API**: http://localhost:8005
- **Documentación**: http://localhost:8005/docs
- **Health**: http://localhost:8005/health

### **Docker**
- **API**: http://localhost:8005
- **Documentación**: http://localhost:8005/docs
- **Health**: http://localhost:8005/health
- **PgAdmin**: http://localhost:5050 (admin@admin.com / admin)

## 💡 Tips y Trucos

### **Desarrollo Local**
- Usa **SQLite** para rapidez
- **Sin Redis** para simplicidad
- **Logs detallados** para debug
- **Hot reload** automático

### **Docker**
- **PostgreSQL** para robustez
- **Redis** para cache
- **Workers** para procesamiento
- **Nginx** para producción

### **Migración**
- **Backup** de configuración
- **Verificar** todas las dependencias
- **Probar** con datos reales
- **Monitorear** logs

---

**¡Desarrolla local, produce con Docker! 🚀**
