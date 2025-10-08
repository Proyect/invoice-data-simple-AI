# Flujo de Desarrollo: Local → Docker 🚀

Guía completa para desarrollar localmente con entorno virtual y luego migrar a Docker para producción.

## 🎯 Estrategia de Desarrollo

### **Fase 1: Desarrollo Local (Entorno Virtual)**
- ✅ Desarrollo rápido y iterativo
- ✅ Debug fácil
- ✅ Sin dependencias complejas
- ✅ Pruebas inmediatas

### **Fase 2: Producción (Docker)**
- ✅ Entorno consistente
- ✅ Despliegue fácil
- ✅ Escalabilidad
- ✅ Todas las dependencias incluidas

## 🐍 Fase 1: Desarrollo Local

### **Configuración Inicial**

```bash
# 1. Configurar entorno virtual
make setup-venv

# 2. Activar entorno virtual
source .venv/bin/activate

# 3. Iniciar desarrollo
make dev-venv
```

### **Estructura para Desarrollo Local**

```
proyecto/
├── .venv/                   # Entorno virtual (local)
├── src/                     # Código fuente
├── uploads/                 # Archivos de prueba
├── data/                    # SQLite local
├── logs/                    # Logs de desarrollo
├── .env                     # Configuración local
├── requirements-venv.txt    # Dependencias locales
└── tests/                   # Tests locales
```

### **Configuración Local (.env)**

```env
# Desarrollo local - configuración mínima
APP_NAME=Document Extractor API - Dev
DEBUG=True
HOST=0.0.0.0
PORT=8005

# SQLite para desarrollo rápido
DATABASE_URL=sqlite:///./data/documents.db

# Sin Redis para simplificar
REDIS_URL=redis://localhost:6379

# Tesseract local
TESSERACT_CMD=

# APIs opcionales para desarrollo
OPENAI_API_KEY=
GOOGLE_APPLICATION_CREDENTIALS=
AWS_ACCESS_KEY_ID=
```

## 🐳 Fase 2: Migración a Docker

### **Cuando Migrar a Docker**

- ✅ **Funcionalidad básica completada**
- ✅ **Tests pasando**
- ✅ **API estable**
- ✅ **Listo para producción**

### **Proceso de Migración**

```bash
# 1. Preparar para Docker
make setup

# 2. Probar en Docker
make dev

# 3. Verificar funcionamiento
make health
make stats
```

## 🔄 Flujo de Trabajo Completo

### **Día a Día (Desarrollo Local)**

```bash
# Iniciar día de desarrollo
source .venv/bin/activate
make dev-venv

# Desarrollar y probar
# ... hacer cambios en código ...

# Formatear código
make format

# Ejecutar tests
make test

# Ver logs
tail -f logs/app.log
```

### **Preparar para Producción (Docker)**

```bash
# 1. Commitear cambios
git add .
git commit -m "feat: nueva funcionalidad"

# 2. Migrar a Docker
make setup

# 3. Probar en Docker
make dev

# 4. Verificar todo funciona
curl http://localhost:8005/health
```

## 📋 Checklist de Migración

### **Antes de Migrar a Docker**

- [ ] **Código estable** - Sin errores críticos
- [ ] **Tests pasando** - `make test` exitoso
- [ ] **Variables de entorno** - `.env` configurado
- [ ] **Dependencias** - `requirements.txt` actualizado
- [ ] **Documentación** - README actualizado

### **Después de Migrar a Docker**

- [ ] **Contenedores funcionando** - `docker-compose ps`
- [ ] **API respondiendo** - `make health`
- [ ] **Base de datos** - Conexión exitosa
- [ ] **Logs limpios** - Sin errores críticos
- [ ] **Performance** - Tiempos de respuesta OK

## 🛠️ Comandos por Fase

### **Desarrollo Local**

```bash
# Configuración
make setup-venv          # Configurar entorno virtual
make install             # Instalar dependencias

# Desarrollo
make dev-venv            # Iniciar aplicación
make venv-shell          # Shell en entorno virtual
make test                # Ejecutar tests
make format              # Formatear código
make lint                # Linting

# Debug
tail -f logs/app.log     # Ver logs
python -c "import sys; print(sys.path)"  # Verificar Python path
```

### **Migración a Docker**

```bash
# Configuración
make setup               # Configurar Docker
make build               # Construir imágenes

# Producción
make dev                 # Desarrollo con Docker
make prod                # Producción
make logs                # Ver logs
make shell               # Shell en contenedor

# Monitoreo
make health              # Health check
make stats               # Estadísticas
make status              # Estado contenedores
```

## 🔧 Configuraciones Específicas

### **Desarrollo Local (.env)**

```env
# Configuración mínima para desarrollo
DEBUG=True
DATABASE_URL=sqlite:///./data/documents.db
REDIS_URL=redis://localhost:6379
TESSERACT_CMD=

# APIs opcionales
OPENAI_API_KEY=
GOOGLE_APPLICATION_CREDENTIALS=
AWS_ACCESS_KEY_ID=
```

### **Docker (.env)**

```env
# Configuración completa para Docker
DEBUG=False
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/document_extractor
REDIS_URL=redis://redis:6379

# APIs configuradas
OPENAI_API_KEY=sk-...
GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json
AWS_ACCESS_KEY_ID=AKIA...
```

## 🚀 Scripts de Transición

### **Script: Local a Docker**

```bash
#!/bin/bash
echo "🔄 Migrando de desarrollo local a Docker..."

# 1. Verificar código estable
echo "🔍 Verificando código..."
if ! make test; then
    echo "❌ Tests fallando. Corrige antes de migrar."
    exit 1
fi

# 2. Commitear cambios
echo "💾 Commiteando cambios..."
git add .
git commit -m "feat: migración a Docker"

# 3. Configurar Docker
echo "🐳 Configurando Docker..."
make setup

# 4. Probar en Docker
echo "🧪 Probando en Docker..."
make dev

# 5. Verificar funcionamiento
echo "✅ Verificando funcionamiento..."
sleep 10
if make health; then
    echo "🎉 Migración exitosa!"
else
    echo "❌ Error en migración"
    exit 1
fi
```

### **Script: Docker a Local**

```bash
#!/bin/bash
echo "🔄 Regresando a desarrollo local..."

# 1. Detener Docker
echo "⏹️ Deteniendo Docker..."
make stop

# 2. Activar entorno virtual
echo "🐍 Activando entorno virtual..."
source .venv/bin/activate

# 3. Iniciar local
echo "🚀 Iniciando desarrollo local..."
make dev-venv
```

## 📊 Comparación de Ambientes

| Aspecto | Desarrollo Local | Docker |
|---------|------------------|---------|
| **Velocidad de inicio** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Debug** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Consistencia** | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Portabilidad** | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Recursos** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Producción** | ⭐⭐ | ⭐⭐⭐⭐⭐ |

## 🎯 Mejores Prácticas

### **Durante Desarrollo Local**

1. **Usar SQLite** para rapidez
2. **Sin Redis** para simplicidad
3. **Tesseract local** para pruebas
4. **Logs detallados** para debug
5. **Tests frecuentes**

### **Durante Migración a Docker**

1. **Verificar todas las dependencias**
2. **Probar con datos reales**
3. **Monitorear performance**
4. **Verificar logs**
5. **Tests de integración**

## 🚨 Troubleshooting

### **Problemas Comunes en Migración**

#### **Error: Base de datos no conecta**
```bash
# Verificar PostgreSQL en Docker
docker-compose logs postgres

# Verificar variables de entorno
docker-compose exec app env | grep DATABASE
```

#### **Error: Redis no disponible**
```bash
# Verificar Redis en Docker
docker-compose logs redis

# Probar conexión
docker-compose exec app redis-cli ping
```

#### **Error: Tesseract no encontrado**
```bash
# Verificar instalación en contenedor
docker-compose exec app tesseract --version

# Verificar configuración
docker-compose exec app env | grep TESSERACT
```

## 📈 Roadmap de Desarrollo

### **Semana 1-2: Desarrollo Local**
- [ ] Configurar entorno virtual
- [ ] Implementar funcionalidad básica
- [ ] Tests unitarios
- [ ] Documentación

### **Semana 3: Migración a Docker**
- [ ] Configurar Docker
- [ ] Migrar base de datos
- [ ] Probar en contenedores
- [ ] Optimizar configuración

### **Semana 4: Producción**
- [ ] Deploy en servidor
- [ ] Monitoreo
- [ ] Performance tuning
- [ ] Documentación final

---

**¡Desarrolla local, produce con Docker! 🚀**
