# Manual para Desarrolladores

Guía técnica para desarrolladores que trabajan en el proyecto.

## 📐 Arquitectura

### Estructura del Código

```
src/app/
├── core/              # Configuración central
│   ├── config.py      # Settings con pydantic-settings
│   ├── database.py    # Conexión DB (PostgreSQL/SQLite)
│   ├── environment.py # Gestión de ambientes
│   └── logging_config.py
├── models/            # Modelos SQLAlchemy ORM
│   ├── document_enhanced.py
│   ├── user_enhanced.py
│   └── ...
├── schemas/           # Esquemas Pydantic v2 (validación/DTO)
│   ├── document_consolidated.py
│   └── ...
├── services/          # Lógica de negocio
│   ├── optimal_ocr_service.py
│   ├── intelligent_extraction_service.py
│   ├── afip_invoice_extraction_service.py
│   ├── academic_document_extraction_service.py
│   └── ...
├── repositories/      # Capa de acceso a datos (Repository Pattern)
│   └── document_repository.py
├── api/               # Endpoints organizados por versión
│   ├── v1/            # API Legacy (mantenimiento)
│   └── v2/            # API Actual (recomendada)
├── routes/            # Endpoints legacy (deprecar gradualmente)
├── auth/              # Autenticación JWT
│   ├── jwt_handler.py
│   ├── password_handler.py
│   └── dependencies.py
└── middleware/        # Middleware personalizado
    ├── error_handler.py
    ├── performance.py
    └── security.py
```

### Patrones de Diseño

- **Repository Pattern**: Abstracción de acceso a datos
- **Service Layer**: Lógica de negocio separada
- **Dependency Injection**: FastAPI dependencies
- **Strategy Pattern**: Múltiples servicios OCR/extracción

## 🔧 Configuración Avanzada

### Variables de Entorno Completas

```env
# Base de datos
DATABASE_URL=postgresql://user:pass@host:5432/db
DATABASE_URL_FALLBACK=sqlite:///./data/documents.db
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# OCR
TESSERACT_CMD=/usr/bin/tesseract
GOOGLE_VISION_DAILY_LIMIT=200
AWS_TEXTRACT_DAILY_LIMIT=100

# LLM
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=1000

# Seguridad
SECRET_KEY=...
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Procesamiento asíncrono
RQ_WORKER_TIMEOUT=600
RQ_QUEUE_NAME=document_processing
```

### Ambientes

El sistema soporta tres ambientes:
- **development**: Debug activado, CORS abierto
- **testing**: Configuración para tests
- **production**: Seguridad reforzada, CORS restringido

## 💻 Desarrollo Local

### Setup Inicial

```bash
# 1. Clonar y entrar al proyecto
cd invoice-data-simple-AI

# 2. Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Instalar modelo de spaCy
python -m spacy download es_core_news_sm

# 5. Configurar .env
cp env.example .env
# Editar .env

# 6. Inicializar base de datos
alembic upgrade head

# 7. Crear usuario admin (opcional)
python create_admin_user.py
```

### Workflow de Desarrollo

```bash
# Iniciar servidor con hot-reload
python main.py
# O con uvicorn directamente
uvicorn app.main:app --reload --port 8005

# Ejecutar tests
pytest tests/ -v

# Ejecutar migraciones
alembic revision -m "descripcion_cambio"
alembic upgrade head

# Ver logs
tail -f logs/app.log
```

### Base de Datos y Migraciones

```bash
# Crear nueva migración
alembic revision -m "nombre_migracion"

# Aplicar migraciones
alembic upgrade head

# Revertir última migración
alembic downgrade -1

# Ver historial
alembic history
```

## 🧪 Testing

### Ejecutar Tests

```bash
# Todos los tests
pytest tests/ -v

# Tests específicos
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/e2e/ -v

# Con cobertura
pytest tests/ --cov=src/app --cov-report=html

# Test específico
pytest tests/test_documents.py::test_create_document -v
```

### Estructura de Tests

```
tests/
├── unit/              # Tests unitarios (componentes aislados)
├── integration/       # Tests de integración (servicios combinados)
├── e2e/               # Tests end-to-end (flujo completo)
├── fixtures/          # Datos de prueba
├── utils/             # Utilidades para tests
└── conftest.py        # Configuración pytest
```

## 📚 Referencia de Endpoints

### API v1 (Legacy)

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/v1/upload` | POST | Upload simple |
| `/api/v1/upload-flexible` | POST | Upload con métodos seleccionables |
| `/api/v1/documents` | GET | Listar documentos |
| `/api/v1/documents/{id}` | GET | Obtener documento |
| `/api/v1/health` | GET | Health check |

### API v2 (Actual)

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/v2/documents/` | GET | Listar con filtros |
| `/api/v2/documents/` | POST | Crear documento |
| `/api/v2/documents/{id}` | GET | Obtener documento |
| `/api/v2/documents/{id}` | PUT | Actualizar documento |
| `/api/v2/documents/{id}` | DELETE | Eliminar documento |
| `/api/v2/documents/search` | POST | Búsqueda avanzada |
| `/api/v2/documents/{id}/process` | POST | Procesar documento |
| `/api/v2/documents/{id}/review` | POST | Revisar documento |
| `/api/v2/documents/batch` | POST | Operaciones en lote |
| `/api/v2/documents/export` | POST | Exportar documentos |
| `/api/v2/documents/stats/overview` | GET | Estadísticas |
| `/api/v2/uploads/` | POST | Subir archivo |

### Autenticación

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/auth/register` | POST | Registrar usuario |
| `/auth/login` | POST | Iniciar sesión |
| `/auth/refresh` | POST | Renovar token |
| `/auth/me` | GET | Usuario actual |

## 🔨 Servicios Clave

### OCR Services

- **OptimalOCRService**: Selección automática del mejor OCR
- **SpecializedOCRService**: OCR con preprocesamiento avanzado

### Extraction Services

- **BasicExtractionService**: Regex + spaCy básico
- **IntelligentExtractionService**: LLM + NLP avanzado
- **AFIPInvoiceExtractionService**: Especializado en facturas AFIP
- **AcademicDocumentExtractionService**: Documentos académicos
- **DNIExtractionService**: DNI argentinos

### Validation Services

- **UniversalValidationService**: Validación genérica
- **AFIPValidationService**: Validación CAE AFIP

## 🏗️ Agregar Nuevas Funcionalidades

### 1. Agregar Nuevo Endpoint

```python
# En src/app/api/v2/nuevo_endpoint.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..core.database import get_db

router = APIRouter()

@router.get("/nuevo")
async def nuevo_endpoint(db: Session = Depends(get_db)):
    return {"message": "Nuevo endpoint"}
```

### 2. Agregar Nuevo Servicio

```python
# En src/app/services/nuevo_servicio.py
class NuevoServicio:
    def __init__(self):
        pass
    
    def procesar(self, data):
        # Lógica aquí
        return resultado
```

### 3. Agregar Nuevo Modelo

```python
# En src/app/models/nuevo_modelo.py
from ..core.database import Base
from sqlalchemy import Column, Integer, String

class NuevoModelo(Base):
    __tablename__ = "nuevo_modelo"
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(255))
```

Luego crear migración:
```bash
alembic revision -m "add_nuevo_modelo"
alembic upgrade head
```

## 📝 Buenas Prácticas

- **Rutas finas**: Lógica en servicios, no en endpoints
- **Validación**: Usar Pydantic v2 para validación
- **Manejo de errores**: HTTPException con mensajes claros
- **Logging**: Usar logger en lugar de print
- **Tests**: Escribir tests al agregar features
- **Type hints**: Usar tipos en todas las funciones
- **Docstrings**: Documentar funciones públicas

## 🐛 Debugging

### Ver Logs

```bash
# Logs de la aplicación
tail -f logs/app.log

# Logs de errores
tail -f logs/error.log

# Logs del sistema
tail -f logs/system.log
```

### Debug en Código

```python
import logging
logger = logging.getLogger(__name__)

logger.debug("Mensaje de debug")
logger.info("Información")
logger.warning("Advertencia")
logger.error("Error")
```

## 🔍 Troubleshooting Técnico

### Problemas Comunes

**Import errors:**
- Verificar que `src` esté en `PYTHONPATH`
- Verificar estructura de imports relativos

**Database errors:**
- Verificar conexión: `python -c "from src.app.core.database import create_database_engine; create_database_engine()"`
- Verificar migraciones: `alembic current`

**Redis errors:**
- El sistema funciona sin Redis (degradado)
- Verificar conexión: `redis-cli ping`

## 🤝 Contribución

### Cómo Contribuir

1. **Fork el proyecto** en GitHub
2. **Crear una rama** para tu feature:
   ```bash
   git checkout -b feature/nueva-funcionalidad
   ```
3. **Hacer cambios** siguiendo las buenas prácticas:
   - Escribir tests para nuevas funcionalidades
   - Mantener cobertura de código
   - Seguir convenciones de código (PEP 8)
   - Documentar funciones públicas
4. **Commit con mensajes claros**:
   ```bash
   git commit -m 'feat: agregar nueva funcionalidad X'
   ```
5. **Push a tu fork**:
   ```bash
   git push origin feature/nueva-funcionalidad
   ```
6. **Abrir Pull Request** en GitHub con descripción clara

### Convenciones de Código

- **Type hints**: Usar en todas las funciones
- **Docstrings**: Documentar clases y funciones públicas
- **Tests**: Escribir tests unitarios e integración
- **Nombres**: Usar nombres descriptivos en inglés
- **Imports**: Organizar imports (stdlib, third-party, local)

### Estructura de Commits

Usar formato Conventional Commits:
- `feat:` Nueva funcionalidad
- `fix:` Corrección de bug
- `docs:` Cambios en documentación
- `test:` Agregar o modificar tests
- `refactor:` Refactorización de código
- `chore:` Tareas de mantenimiento

### Proceso de Revisión

- Todos los PRs requieren al menos una aprobación
- Los tests deben pasar antes de merge
- El código debe seguir las convenciones establecidas
- Se puede solicitar cambios antes de aprobar

## 📖 Recursos Adicionales

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/
- **Pydantic v2**: https://docs.pydantic.dev/
- **Alembic**: https://alembic.sqlalchemy.org/

---

Para más información sobre el proyecto, ver [README.md](README.md)
