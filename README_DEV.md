# Manual para Desarrolladores

## Visión General
Este proyecto implementa una API completa de extracción y gestión de documentos basada en FastAPI, con OCR, extracción inteligente, validación, autenticación JWT, base de datos SQL (SQLite/PostgreSQL), cache con Redis y procesamiento asíncrono.

- Backend: `src/app/`
- Frontend: `frontend/`
- Infra: Docker y Docker Compose

## Arquitectura
- `src/app/core/`: configuración (`config.py`), base de datos (`database.py`)
- `src/app/auth/`: autenticación y dependencias (`jwt_handler.py`, `password_handler.py`, `dependencies.py`)
- `src/app/models/`: modelos ORM de SQLAlchemy (`document.py`, `user.py`, variantes enhanced)
- `src/app/schemas/`: Pydantic v2 para validación/DTO
- `src/app/services/`: lógica de negocio (OCR, extracción inteligente, validación, async, cache)
- `src/app/routes/`: routers FastAPI por dominio (documentos, uploads, auth)
- `src/app/main.py`: inicialización de la app y registro

## Requisitos
- Python 3.13
- (Opcional) Tesseract OCR instalado y en PATH
- (Opcional) Redis para cache/colas
- (Opcional) PostgreSQL para producción

## Configuración
Variables gestionadas con `pydantic-settings` en `src/app/core/config.py`. Crear `.env` (puedes copiar `env.example`).

Claves relevantes:
- `DATABASE_URL` (PostgreSQL) y `DATABASE_URL_FALLBACK` (SQLite)
- `SECRET_KEY`, `ALGORITHM`, expiraciones de tokens
- Redis: `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`
- OCR/LLM: `TESSERACT_CMD`, `OPENAI_API_KEY`, `AWS_*`, `GOOGLE_APPLICATION_CREDENTIALS`

## Instalación
```bash
pip install -r requirements.txt
```

## Base de Datos y Migraciones
- Dev por defecto: SQLite en `data/documents.db` (auto-config).
- Producción: usar `DATABASE_URL` con PostgreSQL.
- Migraciones Alembic:
```bash
alembic revision -m "mi_cambio"
alembic upgrade head
alembic downgrade -1
```

## Ejecución Local
```bash
python main.py
# Docs: http://localhost:8005/docs
```

Con Docker Compose (API + Redis + Postgres + Frontend):
```bash
docker compose up --build
```

## Autenticación JWT
- Archivos: `src/app/auth/jwt_handler.py`, `dependencies.py`, `password_handler.py`.
- Flujo:
  - `POST /auth/login` => devuelve `access_token` (corto) y `refresh_token` (largo).
  - Rutas protegidas usan `Authorization: Bearer <access_token>`.
  - Refresh para renovar tokens.

## Servicios Clave
- OCR: `optimal_ocr_service.py`, `specialized_ocr_service.py`, `basic_extraction_service.py`
- Extracción Inteligente: `intelligent_extraction_service.py` (spaCy + OpenAI opcional)
- Validación: `afip_validation_service.py`, `universal_validation_service.py`
- Async: `async_processing_service.py` (procesamiento en background y actualización en DB)
- Cache: `cache_service.py` (Redis con fallback seguro)

## Endpoints Principales (Cheat‑Sheet)

### Autenticación
- POST `/auth/register` (opcional según configuración)
- POST `/auth/login`
  - Request:
    ```json
    { "email": "user@example.com", "password": "secret" }
    ```
  - Response:
    ```json
    {
      "access_token": "...",
      "refresh_token": "...",
      "token_type": "bearer",
      "expires_in": 1800
    }
    ```
- POST `/auth/refresh`
  - Header: `Authorization: Bearer <refresh_token>`
  - Response: nuevo `access_token`

### Subida y Procesamiento de Documentos
- POST `/upload-optimized`
  - Form-Data: `file` (UploadFile), `document_type` (opcional)
  - Response ejemplo:
    ```json
    {
      "document_type": "FACTURA",
      "confidence": 0.92,
      "entities": {"cuit_emisor": "30-12345678-9"},
      "structured_data": {"total": 1234.56, "moneda": "ARS"},
      "metadata": {"pages": 1}
    }
    ```
- POST `/uploads` o `/simple-upload` según variantes (ver `src/app/routes/`)

### Documentos
- GET `/documents?skip=0&limit=10&search=texto`
  - Response paginada con cache Redis

## Testing y Validación

### Tests Automatizados
```bash
# Ejecutar todos los tests
pytest -q

# Tests específicos
pytest tests/test_documents.py -v
pytest tests/test_services.py -v
pytest tests/test_security.py -v
pytest test_upload.py -v
pytest test_specialized_ocr.py -v
pytest test_universal_validation.py -v
```

### Validación Completa del Sistema
```bash
# Verificación completa (requiere servidor corriendo)
python verificacion_sistema_completo.py

# Validación final de producción
python validacion_sistema_final.py

# Validación básica
python validacion_sistema_completo.py
```

### Tests de Endpoints Específicos
```bash
# Test de upload básico
python test_upload.py

# Test de OCR especializado
python test_specialized_ocr.py

# Test de validación universal
python test_universal_validation.py
```

### Cobertura de Tests
- **Rutas**: upload, documentos, autenticación
- **Servicios**: OCR, extracción, validación, cache
- **Seguridad**: JWT, contraseñas, permisos
- **Integración**: base de datos, Redis, APIs externas
- **Frontend**: funcionalidad básica

## Buenas Prácticas
- Rutas finas; lógica en `services`.
- Validación con Pydantic v2 y respuestas tipadas.
- Manejo de errores con `HTTPException` y logs.
- Escribir tests al agregar features.
- Mantener migraciones sincronizadas con modelos.

## Casos de Uso Específicos

### Procesamiento de Facturas AFIP
```bash
# Upload con detección automática AFIP
curl -X POST "http://localhost:8005/upload-optimized" \
  -F "file=@factura_afip.pdf" \
  -F "document_type=FACTURA"

# Validación específica AFIP
curl -X POST "http://localhost:8005/api/v2/documents/123/process" \
  -H "Content-Type: application/json" \
  -d '{"ocr_provider": "tesseract", "extraction_method": "afip_specialized"}'
```

### Procesamiento por Lotes
```bash
# Múltiples documentos
curl -X POST "http://localhost:8005/upload-batch" \
  -F "files=@doc1.pdf" \
  -F "files=@doc2.pdf" \
  -F "document_type=FACTURA"

# Operaciones en lote v2
curl -X POST "http://localhost:8005/api/v2/documents/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "document_ids": [1,2,3],
    "operation": "update_status",
    "parameters": {"status": "processed"}
  }'
```

### Exportación de Datos
```bash
# Exportar a CSV
curl -X POST "http://localhost:8005/api/v2/documents/export" \
  -H "Content-Type: application/json" \
  -d '{"format": "csv", "include_extracted_data": true}' \
  -o "export.csv"

# Exportar a JSON
curl -X POST "http://localhost:8005/api/v2/documents/export" \
  -H "Content-Type: application/json" \
  -d '{"format": "json", "document_ids": [1,2,3]}'
```

## Extender el Sistema
1. **Modelos**: Agrega/ajusta en `models/` y crea migraciones
2. **Schemas**: Define/actualiza en `schemas/` con validaciones Pydantic v2
3. **Servicios**: Implementa lógica de negocio en `services/`
4. **Rutas**: Expón endpoints en `routes/` con autenticación apropiada
5. **Tests**: Cubre con tests unitarios e integración en `tests/` y `test_*.py`
6. **Validación**: Añade casos de prueba en scripts de validación del sistema

## Administración del Sistema

### Gestión de Usuarios
```bash
# Crear usuario administrador
python create_admin_user.py

# Crear admin simple
python create_simple_admin.py

# Actualizar contraseña de admin
python update_admin_password.py
```

### Scripts de Utilidad
```bash
# Crear facturas de prueba AFIP
python create_afip_invoice_test.py
python create_invoice_with_cae.py
python create_realistic_afip_invoice.py

# Crear documentos de prueba
python create_test_documents.py

# Validación end-to-end
python validacion_sistema_completo.py
python verificacion_sistema_completo.py
```

### Monitoreo y Diagnóstico
```bash
# Verificar estado del sistema
curl http://localhost:8005/health

# Estadísticas de documentos
curl http://localhost:8005/documents/stats

# Estado de la cola de procesamiento
curl http://localhost:8005/queue/stats

# Test de OCR
curl http://localhost:8005/upload/test
```

## Problemas Comunes

### Base de Datos
- **Postgres off**: fallback automático a SQLite
- **Migraciones pendientes**: ejecutar `alembic upgrade head`
- **Conexión rechazada**: verificar credenciales y host

### Servicios Externos
- **Redis off**: cache/async degradan con logs de advertencia
- **Tesseract no instalado**: usar servicios de nube o configurar `TESSERACT_CMD`
- **OpenAI/Cloud sin clave**: extracción inteligente funciona en modo reducido

### OCR y Procesamiento
- **Texto no extraído**: verificar calidad de imagen, instalar Tesseract
- **Confianza baja**: ajustar umbrales en configuración
- **Procesamiento lento**: usar métodos asíncronos para archivos grandes

### Autenticación
- **Token expirado**: usar refresh token o re-login
- **Permisos insuficientes**: verificar roles de usuario
- **Usuario no encontrado**: crear usuario con scripts de utilidad

## Ejemplos cURL Detallados

### Autenticación

#### Login (OAuth2PasswordRequestForm)
```bash
curl -s -X POST "http://localhost:8005/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=secret"
```

#### Refresh token
```bash
curl -s -X POST "http://localhost:8005/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"<REFRESH_TOKEN>"}'
```

#### Obtener usuario actual
```bash
curl -s "http://localhost:8005/auth/me" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

### Documentos

#### Listado con paginación y búsqueda
```bash
curl -s "http://localhost:8005/documents?skip=0&limit=10&search=factura" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

#### Búsqueda avanzada con ranking
```bash
curl -s "http://localhost:8005/documents/search?q=factura%20AFIP&limit=5"
```

#### Estadísticas de documentos
```bash
curl -s "http://localhost:8005/documents/stats"
```

#### Obtener documento específico
```bash
curl -s "http://localhost:8005/documents/123"
```

#### Obtener solo texto extraído
```bash
curl -s "http://localhost:8005/documents/123/text"
```

#### Obtener solo datos extraídos
```bash
curl -s "http://localhost:8005/documents/123/data"
```

#### Reprocesar documento
```bash
curl -s -X POST "http://localhost:8005/documents/123/reprocess?document_type=FACTURA"
```

### Subida de Documentos

#### Upload optimizado (síncrono/asíncrono según tamaño)
```bash
curl -s -X POST "http://localhost:8005/upload-optimized" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -F "file=@./test_invoice.pdf" \
  -F "document_type=FACTURA"
```

#### Upload asíncrono (siempre en background)
```bash
curl -s -X POST "http://localhost:8005/upload-async" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -F "file=@./large_document.pdf" \
  -F "document_type=FACTURA"
```

#### Upload flexible con métodos específicos
```bash
curl -s -X POST "http://localhost:8005/upload-flexible" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -F "file=@./invoice.pdf" \
  -F "document_type=FACTURA" \
  -F "ocr_method=tesseract" \
  -F "extraction_method=hybrid"
```

#### Upload simple (versión básica)
```bash
curl -s -X POST "http://localhost:8005/upload" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -F "file=@./document.pdf" \
  -F "document_type=factura"
```

#### Upload múltiple en lote
```bash
curl -s -X POST "http://localhost:8005/upload-batch" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -F "files=@./doc1.pdf" \
  -F "files=@./doc2.pdf" \
  -F "document_type=FACTURA"
```

### Procesamiento Asíncrono

#### Estado de trabajo
```bash
curl -s "http://localhost:8005/jobs/job_123/status"
```

#### Estadísticas de cola
```bash
curl -s "http://localhost:8005/queue/stats"
```

#### Reintentar trabajo fallido
```bash
curl -s -X POST "http://localhost:8005/jobs/job_123/retry"
```

### API v2 (Enhanced)

#### Listado con filtros avanzados
```bash
curl -s "http://localhost:8005/api/v2/documents/?page=1&size=20&document_type=FACTURA&min_confidence=0.8&sort_by=created_at&sort_order=desc" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

#### Búsqueda avanzada POST
```bash
curl -s -X POST "http://localhost:8005/api/v2/documents/search" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "factura AFIP",
    "document_type": "FACTURA",
    "date_from": "2024-01-01T00:00:00Z",
    "date_to": "2024-12-31T23:59:59Z",
    "page": 1,
    "size": 10
  }'
```

#### Procesar documento específico
```bash
curl -s -X POST "http://localhost:8005/api/v2/documents/123/process" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "ocr_provider": "tesseract",
    "extraction_method": "hybrid",
    "force_reprocess": false,
    "priority": 5
  }'
```

#### Revisar documento
```bash
curl -s -X POST "http://localhost:8005/api/v2/documents/123/review" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "approve",
    "review_notes": "Documento correcto",
    "confidence_override": 0.95
  }'
```

#### Operaciones en lote
```bash
curl -s -X POST "http://localhost:8005/api/v2/documents/batch" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "document_ids": [123, 124, 125],
    "operation": "update_status",
    "parameters": {"status": "processed"}
  }'
```

#### Exportar documentos (JSON)
```bash
curl -s -X POST "http://localhost:8005/api/v2/documents/export" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "document_ids": [123, 124, 125],
    "format": "json",
    "include_extracted_data": true,
    "include_raw_text": false
  }'
```

#### Exportar documentos (CSV)
```bash
curl -s -X POST "http://localhost:8005/api/v2/documents/export" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "format": "csv",
    "include_extracted_data": true
  }' \
  -o "documents_export.csv"
```

#### Estadísticas generales
```bash
curl -s "http://localhost:8005/api/v2/documents/stats/overview" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

### Utilidades

#### Verificar métodos disponibles
```bash
curl -s "http://localhost:8005/upload-flexible/methods"
```

#### Test de OCR
```bash
curl -s "http://localhost:8005/upload/test"
```

## Playbook de Despliegue (Docker/Postgres/Redis)

### Docker Compose básico
```bash
docker compose up --build -d
docker compose logs -f api
```

### Variables de entorno clave
- `DATABASE_URL=postgresql://postgres:postgres@db:5432/document_extractor`
- `REDIS_HOST=redis`
- `SECRET_KEY=<valor-seguro>`

### Troubleshooting rápido
- API no levanta (migraciones):
  - Ejecuta `alembic upgrade head` dentro del contenedor API.
- Conexión a Postgres rechazada:
  - Verifica servicio `db` arriba: `docker compose ps` y logs: `docker compose logs db`.
  - Revisa credenciales y nombre de host (`db`).
- Redis no disponible:
  - El sistema hace fallback; revisa logs y asegúrate de `REDIS_HOST=redis`.
- Errores Tesseract:
  - Instala `tesseract-ocr` en la imagen/base, o configura `TESSERACT_CMD`.
- Problemas de permisos en `uploads/` o `outputs/`:
  - Asegura volúmenes con permisos de escritura para el usuario del contenedor.

### Comandos útiles dentro del contenedor API
```bash
# Abrir shell
docker compose exec api bash

# Aplicar migraciones
alembic upgrade head

# Ejecutar tests
pytest -q
```

## Índice de Endpoints por Router

Nota: Los códigos de estado indicados son los más comunes; algunos endpoints pueden devolver 4xx/5xx ante errores.

### src/app/routes/auth.py
- POST `/register` — público — 201 (crear usuario)
- POST `/login` — público — 200 (tokens)
- POST `/refresh` — público — 200 (nuevo access token)
- GET `/me` — requiere Bearer — 200 (usuario actual)
- PUT `/me` — requiere Bearer — 200 (actualiza usuario)
- POST `/change-password` — requiere Bearer — 200
- GET `/users?skip&limit` — requiere Bearer admin — 200

### src/app/routes/documents.py
- GET `/documents?skip&limit&search` — requiere DB — 200 (lista paginada, cache)
- GET `/documents/search?q&limit` — 200 (búsqueda avanzada; fallback SQLite)
- GET `/documents/stats` — 200 (estadísticas; cache)
- GET `/documents/{document_id}` — 200/404
- DELETE `/documents/{document_id}` — 200/404 (invalida cache)
- GET `/documents/{document_id}/text` — 200/404
- GET `/documents/{document_id}/data` — 200/404
- POST `/documents/{document_id}/reprocess?document_type` — 200 (lanza reproceso async)

### src/app/routes/optimized_upload.py
- POST `/upload-optimized?document_type` — 200 (procesa optimizado, sync/async según tamaño)
- POST `/upload-async?document_type` — 200 (inicia job async)
- GET `/jobs/{job_id}/status` — 200
- GET `/queue/stats` — 200
- POST `/jobs/{job_id}/retry` — 200/400
- POST `/upload-batch?document_type` — 200 (subida múltiple)

### src/app/routes/flexible_upload.py
- POST `/upload-flexible` — 200 (selección de `ocr_method` y `extraction_method`)
- GET `/upload-flexible/methods` — 200 (disponibilidad de métodos)

### src/app/routes/simple_upload.py
- POST `/upload` — 200 (versión simplificada)
- POST `/upload-flexible` — 200 (flexible básico)
- GET `/upload-flexible/methods` — 200
- GET `/upload/test` — 200 (diagnóstico OCR/spaCy)

### src/app/routes/uploads.py
- POST `/upload` — 200 (upload simple con OCR + extracción)
- POST `/upload-flexible` — 200 (métodos auto/básico/inteligente)

### src/app/routes/documents_enhanced.py (prefijo: `/api/v2/documents`)
- POST `/` — 201 — requiere Bearer (crea documento)
- GET `/{document_id}` — 200/404 — requiere Bearer
- PUT `/{document_id}` — 200/404 — requiere Bearer
- DELETE `/{document_id}` — 204/404 — requiere Bearer
- GET `/` — 200 — requiere Bearer (listado con filtros/paginación)
- POST `/search` — 200 — requiere Bearer (búsqueda avanzada)
- POST `/{document_id}/process` — 200 — requiere Bearer (procesamiento)
- POST `/{document_id}/review` — 200 — requiere Bearer (revisión)
- POST `/batch` — 200 — requiere Bearer (operaciones en lote)
- POST `/export` — 200 — requiere Bearer (JSON/CSV/XLSX)
- GET `/stats/overview` — 200 — requiere Bearer
- POST `/upload` — 201 — requiere Bearer (subida con auto-process opcional)

### src/app/routes/documents_enhanced_db.py
- GET `/` — 200 (lista con paginación)
- POST `/` — 200 (crear)
- GET `/{document_id}` — 200/404
- PUT `/{document_id}` — 200/404
- DELETE `/{document_id}` — 200/404
- POST `/search` — 200
- GET `/stats/overview` — 200
- POST `/{document_id}/process` — 200/404
- POST `/batch` — 200

### src/app/routes/documents_enhanced_simple.py
- GET `/` — 200 (mock)
- POST `/` — 200 (mock)
- GET `/{document_id}` — 200 (mock)
- POST `/search` — 200 (mock)
- POST `/{document_id}/process` — 200 (mock)
- POST `/{document_id}/review` — 200 (mock)
- POST `/batch` — 200 (mock)
- POST `/export` — 200 (mock)
- GET `/stats/overview` — 200 (mock)
- PUT `/{document_id}` — 200 (mock)
- POST `/upload` — 200 (mock)
- DELETE `/{document_id}` — 200 (mock)
