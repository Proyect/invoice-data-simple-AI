# Guía de Consolidación de Modelos

## Estado Actual

El proyecto tiene múltiples versiones de modelos de documentos:

### 1. `document.py` - Modelo Básico (Más Usado)
- **Ubicación**: `src/app/models/document.py`
- **Uso**: Modelo principal usado en la mayoría del código
- **Características**:
  - Modelo simple y directo
  - Compatible con SQLite y PostgreSQL
  - Campos básicos: filename, file_path, raw_text, extracted_data
  - Sin relaciones complejas
  - Sin enums (usa strings)

### 2. `document_enhanced.py` - Modelo Mejorado
- **Ubicación**: `src/app/models/document_enhanced.py`
- **Uso**: Usado en algunos servicios y routes enhanced
- **Características**:
  - Enums para tipos, estados, proveedores
  - Relaciones con User y Organization
  - Campos adicionales: uuid, file_hash, quality_score
  - Métodos helper y propiedades híbridas
  - Soporte para búsqueda full-text

### 3. `document_unified.py` - Modelo Unificado
- **Ubicación**: `src/app/models/document_unified.py`
- **Uso**: Menos usado, parece ser un intento de unificación
- **Características**:
  - Usa mixins (TimestampMixin, SoftDeleteMixin, etc.)
  - Enums como strings
  - Diseñado para ser más flexible

### 4. `models_v2.py` - Modelos V2 Completos
- **Ubicación**: `src/app/models/models_v2.py`
- **Uso**: Muy poco usado
- **Características**:
  - Base separada (BaseV2)
  - Modelos completos con todos los enums
  - Diseñado como reemplazo completo

## Análisis de Uso

### Archivos que usan `document.py` (Modelo Básico):
- `src/app/services/async_processing_service.py`
- `src/app/routes/documents.py`
- `src/app/routes/flexible_upload.py`
- `src/app/routes/uploads.py`
- `src/app/api/v1/uploads.py`
- `src/app/repositories/document_repository.py`
- `src/app/routes/simple_upload.py`
- `src/app/routes/optimized_upload.py`

### Archivos que usan `document_enhanced.py`:
- `src/app/services/document_service_enhanced.py`
- `src/app/routes/documents_enhanced.py`
- `src/app/routes/documents_enhanced_db.py`
- `src/app/models/user_enhanced.py` (imports)

## Recomendación de Consolidación

### Opción 1: Migrar todo a `document_enhanced.py` (Recomendado)
**Ventajas**:
- Más completo y funcional
- Ya tiene enums y relaciones
- Mejor estructura para crecimiento futuro

**Desventajas**:
- Requiere migración de base de datos
- Más complejo que el modelo básico

### Opción 2: Mantener `document.py` como base, extender cuando necesario
**Ventajas**:
- Menos cambios necesarios
- Compatible con código existente

**Desventajas**:
- Mantiene duplicación
- No resuelve el problema de múltiples modelos

### Opción 3: Crear nuevo modelo consolidado
**Ventajas**:
- Diseño limpio desde cero
- Puede combinar mejores características

**Desventajas**:
- Más trabajo
- Requiere migración completa

## Plan de Migración Sugerido

1. **Fase 1: Análisis**
   - Identificar todas las dependencias
   - Documentar diferencias de esquema
   - Crear tests de compatibilidad

2. **Fase 2: Preparación**
   - Crear migración de Alembic
   - Crear scripts de migración de datos
   - Actualizar schemas Pydantic

3. **Fase 3: Migración Gradual**
   - Migrar repositories primero
   - Migrar services
   - Migrar routes/API
   - Actualizar tests

4. **Fase 4: Limpieza**
   - Eliminar modelos legacy
   - Actualizar documentación
   - Verificar que todo funciona

## Notas Importantes

- El modelo básico (`document.py`) es el más usado y funciona bien
- `document_enhanced.py` tiene más características pero menos adopción
- La consolidación requiere cuidado para no romper funcionalidad existente
- Considerar mantener compatibilidad durante la transición

## Archivos a Modificar en Consolidación

Si se elige migrar a `document_enhanced.py`:
- `src/app/repositories/document_repository.py`
- `src/app/services/async_processing_service.py`
- `src/app/routes/*.py` (múltiples archivos)
- `src/app/api/v1/uploads.py`
- Migraciones de Alembic
- Tests

