# Guía de Migración de Routes Legacy a API v2

## Estado Actual

Las rutas en `src/app/routes/` están **DEPRECADAS** y se están migrando a API v2 (`src/app/api/v2/`).

## Rutas Legacy y su Equivalente en v2

### 1. `routes/documents.py` → `api/v2/documents.py`
**Funcionalidad**: Listado, búsqueda y estadísticas de documentos

**Endpoints Legacy**:
- `GET /documents` - Listar documentos
- `GET /documents/search` - Búsqueda avanzada
- `GET /documents/stats` - Estadísticas

**Equivalente v2**:
- `GET /api/v2/documents/` - Listar documentos (con filtros mejorados)
- `POST /api/v2/documents/search` - Búsqueda avanzada
- `GET /api/v2/analytics/stats` - Estadísticas (en analytics)

**Migración**:
```python
# Antes (legacy)
GET /documents?skip=0&limit=10&search=test

# Después (v2)
GET /api/v2/documents/?skip=0&limit=20&document_type=factura&status=processed
```

### 2. `routes/uploads.py` → `api/v2/uploads.py`
**Funcionalidad**: Subida básica de documentos

**Endpoints Legacy**:
- `POST /upload` - Subir documento

**Equivalente v2**:
- `POST /api/v2/uploads/` - Subir documento (en desarrollo)

**Nota**: El endpoint v2 está en desarrollo. Usar temporalmente `/api/v1/upload`.

### 3. `routes/simple_upload.py` → `api/v2/uploads.py`
**Funcionalidad**: Subida simple con procesamiento básico

**Endpoints Legacy**:
- `POST /upload-simple` - Subida simple

**Equivalente v2**:
- `POST /api/v2/uploads/` - Subida (cuando esté completo)

### 4. `routes/flexible_upload.py` → `api/v2/uploads.py`
**Funcionalidad**: Subida con selección de métodos OCR y extracción

**Endpoints Legacy**:
- `POST /upload-flexible` - Subida flexible

**Equivalente v2**:
- `POST /api/v2/uploads/` con parámetros de método

### 5. `routes/optimized_upload.py` → `api/v2/uploads.py` + `api/v2/processing.py`
**Funcionalidad**: Subida optimizada y procesamiento asíncrono

**Endpoints Legacy**:
- `POST /upload-optimized` - Subida optimizada
- `POST /upload-async` - Subida asíncrona

**Equivalente v2**:
- `POST /api/v2/uploads/` - Subida
- `POST /api/v2/processing/process` - Procesamiento

### 6. `routes/documents_enhanced.py` → `api/v2/documents.py`
**Funcionalidad**: Documentos mejorados con funcionalidades avanzadas

**Endpoints Legacy**:
- `POST /documents-enhanced/` - Crear documento mejorado
- `GET /documents-enhanced/{id}` - Obtener documento
- `PUT /documents-enhanced/{id}` - Actualizar documento
- `GET /documents-enhanced/` - Listar documentos
- `POST /documents-enhanced/search` - Búsqueda avanzada

**Equivalente v2**:
- Todos los endpoints están en `GET /api/v2/documents/` con schemas consolidados

### 7. `routes/documents_enhanced_db.py` → `api/v2/documents.py`
**Funcionalidad**: Similar a documents_enhanced pero con acceso directo a DB

**Equivalente v2**: Mismo que documents_enhanced

### 8. `routes/documents_enhanced_simple.py` → `api/v2/documents.py`
**Funcionalidad**: Versión simplificada de documents_enhanced

**Equivalente v2**: Mismo que documents_enhanced

### 9. `routes/auth.py` → `api/v2/auth.py`
**Funcionalidad**: Autenticación

**Endpoints Legacy**:
- `POST /auth/login` - Iniciar sesión
- `POST /auth/register` - Registrar usuario

**Equivalente v2**:
- `POST /api/v2/auth/login` - Iniciar sesión
- `POST /api/v2/auth/register` - Registrar usuario

## Plan de Migración

### Fase 1: Identificar Uso (COMPLETADO)
- ✅ Identificadas todas las rutas legacy
- ✅ Documentadas equivalencias en v2

### Fase 2: Completar Endpoints v2 (EN PROGRESO)
- ⏸️ Completar `api/v2/uploads.py` (actualmente solo placeholder)
- ✅ `api/v2/documents.py` - Completo
- ✅ `api/v2/processing.py` - Completo
- ✅ `api/v2/analytics.py` - Completo
- ✅ `api/v2/auth.py` - Completo

### Fase 3: Marcar como Deprecated (COMPLETADO)
- ✅ Agregadas advertencias de deprecación
- ✅ Documentación de migración creada

### Fase 4: Migración Gradual
1. Actualizar clientes para usar v2
2. Mantener legacy por período de transición (3-6 meses)
3. Remover rutas legacy después del período de transición

## Ejemplos de Migración

### Ejemplo 1: Listar Documentos

**Antes (Legacy)**:
```python
GET /documents?skip=0&limit=10&search=factura
```

**Después (v2)**:
```python
GET /api/v2/documents/?skip=0&limit=20&document_type=factura
```

### Ejemplo 2: Subir Documento

**Antes (Legacy)**:
```python
POST /upload-flexible
Content-Type: multipart/form-data

file: documento.pdf
ocr_method: google_vision
extraction_method: hybrid
```

**Después (v2)**:
```python
POST /api/v2/uploads/
Content-Type: multipart/form-data

file: documento.pdf
ocr_provider: google_vision
extraction_method: hybrid
```

### Ejemplo 3: Búsqueda Avanzada

**Antes (Legacy)**:
```python
GET /documents/search?q=factura&limit=10
```

**Después (v2)**:
```python
POST /api/v2/documents/search
Content-Type: application/json

{
  "query": "factura",
  "document_type": "factura",
  "status": "processed",
  "limit": 20
}
```

## Beneficios de Migrar a v2

1. **Schemas Consolidados**: Usa `document_consolidated.py` con validación mejorada
2. **Mejor Organización**: Endpoints agrupados lógicamente
3. **Funcionalidades Mejoradas**: Búsqueda más potente, filtros avanzados
4. **Mejor Documentación**: Swagger docs más completos
5. **Mantenimiento**: Código más limpio y fácil de mantener

## Notas Importantes

- Las rutas legacy seguirán funcionando temporalmente
- Se emitirán advertencias de deprecación en logs
- La migración debe ser gradual para no romper clientes existentes
- Consultar `/api/v2/docs` para documentación completa de v2

## Soporte

Para preguntas sobre la migración:
1. Consultar documentación en `/api/v2/docs`
2. Revisar ejemplos en este documento
3. Contactar al equipo de desarrollo


































