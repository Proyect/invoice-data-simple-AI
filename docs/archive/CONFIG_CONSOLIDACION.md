# Guía de Consolidación de Configuración

## Estado Actual

El proyecto tiene dos sistemas de configuración:

### 1. `config.py` - Configuración Legacy
- **Ubicación**: `src/app/core/config.py`
- **Tipo**: Pydantic Settings simple
- **Uso**: Usado en muchos archivos legacy
- **Características**:
  - Configuración plana (todos los campos en un nivel)
  - Sin validación avanzada
  - Sin soporte para ambientes
  - Crea directorios automáticamente
  - Configura Tesseract automáticamente

### 2. `environment.py` - Configuración Moderna
- **Ubicación**: `src/app/core/environment.py`
- **Tipo**: Pydantic Settings con configuración anidada
- **Uso**: Usado en código nuevo (main.py, database.py, etc.)
- **Características**:
  - Configuración anidada (database, redis, ocr, llm, security)
  - Validación avanzada
  - Soporte para múltiples ambientes (development, testing, staging, production)
  - Mejor organización
  - Validadores personalizados

## Análisis de Uso

### Archivos que usan `config.py`:
- `src/app/services/async_processing_service.py`
- `src/app/services/cache_service.py`
- `src/app/routes/flexible_upload.py`
- `src/app/core/dependencies.py`
- `src/app/api/v1/uploads.py`
- `src/app/routes/optimized_upload.py`
- `src/app/models/document_enhanced.py`
- `src/app/services/intelligent_extraction_service.py`
- `src/app/services/optimal_ocr_service.py`
- `src/app/models/document.py`
- `src/app/services/document_service_enhanced.py`
- `src/app/routes/simple_upload.py`
- `src/app/auth/jwt_handler.py`

### Archivos que usan `environment.py`:
- `src/app/main.py`
- `src/app/core/database.py`
- `src/app/middleware/rate_limiting.py`
- `src/app/middleware/error_handler.py`
- `src/app/core/logging_config.py`
- `src/app/services/cache_optimized.py`
- `src/app/services/async_processing_service.py` (también usa config.py)

## Recomendación

**Migrar todo a `environment.py`** porque:
1. Es más moderno y completo
2. Tiene mejor validación
3. Soporta múltiples ambientes
4. Mejor organización con configuración anidada
5. Ya está siendo usado en código nuevo

## Plan de Migración

### Fase 1: Crear Capa de Compatibilidad
1. Agregar funciones helper en `environment.py` que mapeen a la API de `config.py`
2. Esto permite migración gradual sin romper código existente

### Fase 2: Migrar Archivos Críticos
1. Migrar servicios principales
2. Migrar routes
3. Migrar modelos

### Fase 3: Deprecar config.py
1. Agregar warnings de deprecación
2. Documentar migración
3. Eliminar después de migración completa

## Mapeo de Configuración

### De config.py a environment.py:

```python
# config.py → environment.py
settings.APP_NAME → settings.name
settings.DEBUG → settings.debug
settings.HOST → settings.host
settings.PORT → settings.port
settings.DATABASE_URL → settings.database.url
settings.DATABASE_URL_TEST → settings.database.url_test
settings.DATABASE_URL_FALLBACK → settings.database.url_fallback
settings.REDIS_HOST → settings.redis.host
settings.REDIS_PORT → settings.redis.port
settings.REDIS_DB → settings.redis.db
settings.UPLOAD_DIR → settings.upload_dir
settings.OUTPUT_DIR → settings.output_dir
settings.TESSERACT_CMD → settings.ocr.tesseract_cmd
settings.SECRET_KEY → settings.security.secret_key
settings.ALGORITHM → settings.security.algorithm
settings.ACCESS_TOKEN_EXPIRE_MINUTES → settings.security.access_token_expire_minutes
settings.RQ_WORKER_TIMEOUT → settings.rq_worker_timeout
settings.RQ_QUEUE_NAME → settings.rq_queue_name
```

## Funcionalidades Especiales de config.py

### 1. Creación Automática de Directorios
```python
# En config.py
Path(settings.UPLOAD_DIR).mkdir(exist_ok=True)
Path(settings.OUTPUT_DIR).mkdir(exist_ok=True)
Path("data").mkdir(exist_ok=True)
```

**Solución**: Mover a `main.py` o crear función de inicialización

### 2. Configuración de Tesseract
```python
# En config.py
if settings.TESSERACT_CMD:
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD
```

**Solución**: Mover a inicialización de servicios OCR

## Archivos Prioritarios para Migración

1. **Alta Prioridad**:
   - `src/app/services/async_processing_service.py` (usa ambos)
   - `src/app/services/optimal_ocr_service.py`
   - `src/app/services/intelligent_extraction_service.py`

2. **Media Prioridad**:
   - `src/app/routes/*.py`
   - `src/app/api/v1/uploads.py`
   - `src/app/models/*.py`

3. **Baja Prioridad**:
   - `src/app/auth/jwt_handler.py`
   - `src/app/core/dependencies.py`

## Ejemplo de Migración

### Antes (config.py):
```python
from ..core.config import settings

database_url = settings.DATABASE_URL
redis_host = settings.REDIS_HOST
secret_key = settings.SECRET_KEY
```

### Después (environment.py):
```python
from ..core.environment import get_settings

settings = get_settings()
database_url = settings.database.url
redis_host = settings.redis.host
secret_key = settings.security.secret_key
```

## Notas

- La migración debe ser gradual para no romper funcionalidad
- Considerar mantener `config.py` como wrapper temporal
- Actualizar todos los tests después de migración
- Documentar cambios en CHANGELOG


































