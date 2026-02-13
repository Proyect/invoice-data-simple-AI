# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

## [2.3.0] - 2024-12-XX

### ✅ Mejoras Críticas Implementadas

#### Consolidación de Cache
- **Nuevo**: Creado `src/app/services/cache.py` consolidado
- **Eliminado**: `src/app/services/cache_service.py` (legacy)
- **Eliminado**: `src/app/services/cache_optimized.py` (legacy)
- **Migrado**: Todos los imports actualizados (5 archivos)
- **Características**:
  - Cache multi-nivel (memoria + Redis)
  - Soporte sync/async
  - Decoradores `@cached` y `@cache_invalidate`
  - Fallback automático si Redis no disponible

#### Migración de Configuración
- **Mejorado**: `src/app/core/config.py` ahora es wrapper de compatibilidad
- **Migrado**: 5 archivos críticos a `environment.py`:
  - `optimal_ocr_service.py`
  - `flexible_upload.py`
  - `document_enhanced.py`
  - `document_service_enhanced.py`
  - `dependencies.py`
- **Corregido**: Agregado `extra='ignore'` a todas las configuraciones
- **Corregido**: Inicialización de `DatabaseConfig` con valores por defecto

#### Dependencias
- **Agregado**: `requests==2.31.0` a `requirements.txt`
- **Verificado**: Todas las dependencias declaradas

#### Correcciones de Tests
- **Corregido**: `test_cache.py` para usar nuevo cache consolidado
- **Corregido**: `processing.py` (field_validator → validator)
- **Corregido**: `test_production_system.py` (error de indentación)
- **Actualizado**: Imports de `document_unified` a `document_enhanced` en tests

#### Scripts y Herramientas
- **Nuevo**: `tests/test_critical_fixes.py` - Tests de validación
- **Nuevo**: `scripts/verify_critical_fixes.py` - Script de verificación automatizado

### 📝 Documentación

- **Nuevo**: `ANALISIS_COMPLETO_SISTEMA.md` - Análisis completo del sistema
- **Actualizado**: `CHANGELOG.md` con nuevas mejoras

### 🔧 Cambios Técnicos

#### Backend
- `src/app/services/cache.py` - Servicio consolidado
- `src/app/core/config.py` - Wrapper de compatibilidad con deprecación
- `src/app/core/environment.py` - Mejoras en validación
- `src/app/services/optimal_ocr_service.py` - Migrado a environment.py
- `src/app/routes/flexible_upload.py` - Migrado a environment.py
- `src/app/models/document_enhanced.py` - Limpieza de imports
- `src/app/services/document_service_enhanced.py` - Migrado a environment.py
- `src/app/core/dependencies.py` - Actualizado para nuevo cache
- `src/app/routes/documents.py` - Actualizado para nuevo cache
- `src/app/routes/optimized_upload.py` - Actualizado para nuevo cache
- `src/app/repositories/document_repository.py` - Actualizado para nuevo cache
- `src/app/repositories/base_repository.py` - Actualizado para nuevo cache

#### Tests
- `tests/test_cache.py` - Actualizado para nuevo cache
- `tests/test_models.py` - Actualizado para usar document_enhanced
- `tests/test_repositories.py` - Actualizado para usar document_enhanced
- `tests/test_optimized_system.py` - Actualizado para nuevo cache
- `tests/conftest.py` - Actualizado para usar document_enhanced
- `tests/test_production_system.py` - Corregido error de indentación

#### Schemas
- `src/app/schemas/processing.py` - Corregido uso de validator

### 🐛 Correcciones

- Corregido error de validación Pydantic en `environment.py`
- Corregido error de import en tests que usaban cache_optimized
- Corregido error de import en tests que usaban document_unified
- Corregido error de indentación en test_production_system.py
- Corregido uso de field_validator en processing.py

### 📊 Impacto

- **Eliminada duplicación**: Cache consolidado en un solo servicio
- **Mejorada consistencia**: Configuración migrada a sistema moderno
- **Aumentada calidad**: Tests corregidos y validación agregada
- **Mejorada mantenibilidad**: Código más limpio y organizado

### 🔄 Deprecaciones

- `src/app/services/cache_service.py` - Eliminado (usar `cache.py`)
- `src/app/services/cache_optimized.py` - Eliminado (usar `cache.py`)
- `src/app/core/config.py` - Deprecado (usar `environment.py`)

## [2.2.0] - 2025-12-02

### ✅ Mejoras Implementadas

#### Correcciones Críticas
- **Configuración Pydantic**: Agregado `extra='ignore'` en `AppConfig` para permitir variables de entorno no definidas
- **API Redis Queue**: Removido import obsoleto de `Connection` desde `rq`
- **Dependencias**: Agregado `pytest-cov` para reportes de cobertura
- **Schemas**: Corregidos validadores para usar mensajes en español

#### Mejoras de Código
- **Manejo de Errores**: Agregados códigos de error personalizados y mensajes más informativos
- **Sistema de Métricas**: Implementado middleware básico de métricas con endpoint `/metrics`
- **Optimización de Queries**: Mejorado método `get_stats()` en DocumentRepository
- **Frontend**: Mejorado manejo de errores con mensajes específicos por código HTTP

#### Documentación
- Consolidada documentación técnica en carpeta `docs/`
- Creadas guías de migración y consolidación
- Actualizado README principal con referencias

#### Infraestructura
- Removida advertencia obsoleta de Docker Compose (versión)
- Routes legacy marcadas como deprecated con advertencias

### 📝 Documentación

- `docs/MODELOS_CONSOLIDACION.md` - Guía de consolidación de modelos
- `docs/CONFIG_CONSOLIDACION.md` - Guía de consolidación de configuración
- `docs/ROUTES_MIGRATION_GUIDE.md` - Guía de migración de routes
- `docs/DEPENDENCIES_UPDATE_GUIDE.md` - Guía de actualización de dependencias

### 🔧 Cambios Técnicos

#### Backend
- `src/app/core/environment.py` - Configuración Pydantic mejorada
- `src/app/services/async_processing_service.py` - API rq actualizada
- `src/app/schemas/document_consolidated.py` - Validadores mejorados
- `src/app/middleware/error_handler.py` - Manejo de errores mejorado
- `src/app/middleware/metrics.py` - Nuevo sistema de métricas
- `src/app/repositories/document_repository.py` - Queries optimizadas

#### Frontend
- `frontend/src/services/api.js` - Interceptor de errores mejorado
- `frontend/src/components/DocumentUpload.jsx` - Mejor manejo de errores
- `frontend/src/components/DocumentList.jsx` - Mejor manejo de errores y loading

#### Configuración
- `requirements.txt` - pytest-cov agregado
- `docker-compose.yml` - Versión obsoleta removida

### 🐛 Correcciones

- Corregido error de validación Pydantic que bloqueaba tests
- Corregido import obsoleto de rq que causaba errores
- Corregidos validadores de schemas para mensajes en español

### 📊 Nuevas Funcionalidades

- Endpoint `/metrics` para consultar métricas del sistema
- Sistema de códigos de error personalizados
- Mejoras en mensajes de error del frontend

### 🔄 Deprecaciones

- Routes en `src/app/routes/` marcadas como deprecated
- Se recomienda migrar a API v2 (`/api/v2/`)

## [2.1.0] - Versión Anterior

Ver historial anterior en commits de git.
