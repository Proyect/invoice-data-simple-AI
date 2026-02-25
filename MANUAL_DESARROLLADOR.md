# Manual del desarrollador — Document Extractor API

Guía técnica para desarrollar y mantener el proyecto.

---

## Arquitectura

### Estructura del código

```
src/app/
├── core/                    # Configuración y base
│   ├── environment.py      # Config por ambiente (Pydantic)
│   ├── database.py         # PostgreSQL/SQLite, Redis
│   ├── dependencies.py     # Inyección de dependencias (FastAPI)
│   └── logging_config.py
├── models/                  # ORM SQLAlchemy
│   ├── document.py         # Document + DocumentStatusValues (tabla documents)
│   ├── models_v2.py        # Modelos v2 (documents_v2, users_v2, etc.)
│   └── ...
├── schemas/                 # Pydantic v2 (validación, DTO)
│   ├── document_consolidated.py
│   └── ...
├── services/                # Lógica de negocio
│   ├── afip/               # Extracción facturas AFIP (modular)
│   │   ├── afip_invoice_data.py
│   │   ├── afip_patterns.py
│   │   ├── afip_validators.py
│   │   └── afip_text_extractor.py
│   ├── afip_invoice_extraction_service.py  # Orquestador AFIP + OCR
│   ├── optimal_ocr_service.py
│   ├── intelligent_extraction_service.py
│   ├── cache.py            # Cache multi-nivel (memoria + Redis)
│   └── ...
├── repositories/            # Acceso a datos (Repository)
│   ├── base_repository.py
│   └── document_repository.py  # Usa models.document.Document
├── api/
│   ├── v1/                 # API legacy
│   └── v2/                 # API actual (documents, uploads, auth, etc.)
├── auth/                    # JWT, contraseñas
├── middleware/              # Errores, seguridad, métricas, rate limit
└── main.py                  # FastAPI app, lifespan, rutas
```

### Patrones

- **Repository**: `DocumentRepository` sobre `Document` (tabla `documents`).
- **Servicios**: Lógica en `services/`; endpoints finos que delegan.
- **DI**: FastAPI `Depends()`; providers en `core/dependencies.py` (sin `@lru_cache` en los que reciben `Depends` o Session).
- **Config**: Un solo origen en `core/environment.py`; producción exige `SECRET_KEY` distinto del valor por defecto.

---

## Configuración de desarrollo

### Variables de entorno

```env
DATABASE_URL=postgresql://user:pass@localhost:5432/document_extractor
DATABASE_URL_FALLBACK=sqlite:///./data/documents.db
REDIS_HOST=localhost
REDIS_PORT=6379
SECRET_KEY=clave-desarrollo
ENVIRONMENT=development
DEBUG=True
OPENAI_API_KEY=sk-...   # opcional
```

### Setup local

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows | source .venv/bin/activate  # Linux/mac
pip install -r requirements.txt
python -m spacy download es_core_news_sm
cp env.example .env
# Si usas PostgreSQL/Redis en Docker: docker-compose up -d postgres redis
alembic upgrade head
python main.py
```

Con hot-reload (desde raíz, `PYTHONPATH=src`):

```bash
PYTHONPATH=src uvicorn app.main:app --reload --host 0.0.0.0 --port 8005
```

O usar el script: `scripts/run-local-backend.bat` (Windows) o `./scripts/run-local-backend.sh` (Linux/mac).

---

## Base de datos y migraciones

- **Modelo principal para documentos**: `src/app/models/document.py` (tabla `documents`). Constantes de estado: `DocumentStatusValues`.
- **Migraciones**: Alembic en `alembic/versions/`.

```bash
alembic upgrade head
alembic revision -m "descripcion"
alembic downgrade -1
alembic history
```

---

## Tests

```bash
pytest tests/ -v
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/ --cov=src/app --cov-report=html --cov-report=term
```

Estructura: `tests/unit/`, `tests/integration/`, `tests/e2e/`, `tests/conftest.py`, `tests/fixtures/`.

---

## API de referencia rápida

- **v1 (legacy)**: `/api/v1/upload`, `/api/v1/documents`, etc.
- **v2**: `/api/v2/documents/`, `/api/v2/uploads/`, `/api/v2/processing/`, `/api/v2/analytics/`, `/api/v2/auth/`.
- **Sistema**: `/health`, `/info`, `/metrics`, `/docs`.

Detalle completo en `/docs` con el servidor levantado.

---

## Servicios principales

- **OCR**: `OptimalOCRService`, `SpecializedOCRService`
- **Extracción**: `IntelligentExtractionService`, `AFIPInvoiceExtractionService` (orquesta `afip/` + OCR), `AcademicDocumentExtractionService`, `DNIExtractionService`
- **Validación**: `AFIPValidationService`, `UniversalValidationService`
- **Cache**: `CacheService` en `services/cache.py` (memoria + Redis)
- **Repositorio**: `DocumentRepository` sobre `Document` (document.py)

---

## Añadir funcionalidad

### Nuevo endpoint (v2)

Crear router en `src/app/api/v2/`, registrar en `api/v2/__init__.py`, usar `Depends(get_db)` y servicios desde `core/dependencies.py`.

### Nuevo servicio

Añadir clase en `services/`; si depende de otros servicios, exponer un provider en `core/dependencies.py` (sin `@lru_cache` si usa `Depends` o Session).

### Nuevo modelo

Definir en `models/`, crear migración con `alembic revision -m "..."` y aplicar `alembic upgrade head`.

---

## Buenas prácticas

- Lógica en servicios, no en rutas.
- Validación con Pydantic v2.
- `HTTPException` con mensajes claros.
- Logging con `logging.getLogger(__name__)`.
- Type hints y docstrings en APIs públicas.
- Tests para nuevas funcionalidades.

---

## Modo local vs producción

### Desarrollo local (sin Docker)

1. **Solo backend**
   - Crear `.env` desde `env.example`. Ajustar `DATABASE_URL` (PostgreSQL en puerto 5434 si usas `docker-compose up postgres redis`) y `REDIS_*`.
   - Desde la raíz del proyecto:
     - Windows: `scripts\run-local-backend.bat`
     - Linux/mac: `./scripts/run-local-backend.sh`
   - O manual: `PYTHONPATH=src uvicorn app.main:app --reload --host 0.0.0.0 --port 8005`
   - API en http://localhost:8005 (frontend por defecto apunta a 8006; si corres backend en 8005, en frontend usa `REACT_APP_API_URL=http://localhost:8005`).

2. **Solo frontend**
   - En `frontend/`: copiar `env.example` a `.env`, `npm install` y `npm run start`.
   - Windows: `scripts\run-local-frontend.bat` (desde raíz).

3. **Todo con Docker (recomendado para desarrollo)**
   - `docker-compose up -d` (app en 8006, frontend en 3001, postgres 5434, redis 6380).
   - Frontend: `REACT_APP_API_URL=http://localhost:8006`.

### Producción

- **Variables**: `ENVIRONMENT=production`, `DEBUG=False`, `SECRET_KEY` obligatorio y distinto del valor por defecto (validado al arranque). CORS con orígenes concretos (`CORS_ORIGINS=https://tu-dominio.com`).
- **Stack**: `docker-compose -f docker-compose.prod.yml up -d`. Exportar o usar `--env-file .env.prod` con `SECRET_KEY` y `POSTGRES_PASSWORD` reales.
- **Frontend para prod**: En `frontend/`, build con `REACT_APP_API_URL=` (vacío si nginx hace proxy de `/api` al backend). Ejemplo: `docker build --build-arg REACT_APP_API_URL= -t frontend .`.
- **Migraciones**: Aplicar antes de levantar la app: `alembic upgrade head` (en el contenedor o en el host contra la misma DB).

### Checklist antes de producción

- [ ] `SECRET_KEY` generado seguro (≥32 caracteres), no el valor por defecto.
- [ ] `ENVIRONMENT=production` y `DEBUG=False`.
- [ ] `DATABASE_URL` y `POSTGRES_PASSWORD` seguros; DB con backups.
- [ ] `CORS_ORIGINS` con el dominio real del frontend, no `*`.
- [ ] Migraciones aplicadas (`alembic upgrade head`).
- [ ] Redis accesible y con persistencia si se usa cache/colas.
- [ ] Frontend construido con la `REACT_APP_API_URL` correcta (vacía si mismo origen vía proxy).
- [ ] Health check: `/health` respondiendo correctamente.

---

## Referencias

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://docs.sqlalchemy.org/)
- [Pydantic v2](https://docs.pydantic.dev/)
- [Alembic](https://alembic.sqlalchemy.org/)

---

Para uso del sistema y despliegue, ver **MANUAL_USUARIO.md**. Resumen de procesos local/producción en **docs/PROCESOS_LOCAL_Y_PRODUCCION.md**. Cambios notables en **CHANGELOG.md**.

---

## Si el proyecto requiere cambios (decisiones tuyas)

- **Documentación en producción**: Por defecto `/docs` y `/openapi.json` están deshabilitados cuando `ENVIRONMENT=production`. Si quieres habilitarlos (por ejemplo solo en red interna), hay que exponer una variable (ej. `ENABLE_DOCS_IN_PROD=true`) y usarla en `create_app()` en `src/app/main.py`.
- **Migraciones al arrancar**: Hoy las migraciones no se ejecutan dentro del contenedor al iniciar. Debes ejecutarlas en el pipeline (ej. `alembic upgrade head`) o con un job/script antes de levantar la app. Si prefieres que el contenedor ejecute migraciones al arrancar, se puede añadir un script de entrypoint que llame a `alembic upgrade head` y luego a `python main.py`.
- **Contraseña de PostgreSQL en Compose**: En `docker-compose.prod.yml` se usa `POSTGRES_PASSWORD` desde el entorno. Asegúrate de exportarla o de usar `--env-file .env.prod` con ese valor; si no, se usa el valor por defecto (inseguro en producción).
- **Frontend en producción**: El Compose de producción incluye el servicio `frontend` bajo el perfil `frontend`. Si sirves el frontend con otro nginx o CDN, no hace falta ese servicio; construye con `REACT_APP_API_URL` adecuado y despliega los estáticos donde corresponda.
