# Tutorial Completo: Cómo Proceder con el Proyecto

## 1. Análisis del Proyecto

### 1.1 Descripción General

Sistema profesional de extracción y análisis de documentos con IA que combina:

- **OCR Híbrido**: Tesseract (gratis) + Google Vision + AWS Textract
- **Extracción Inteligente**: Regex + spaCy + OpenAI GPT
- **Base de Datos**: PostgreSQL (producción) / SQLite (desarrollo)
- **Procesamiento Asíncrono**: Redis Queue + Workers
- **API RESTful**: FastAPI con endpoints v1 (legacy) y v2 (actual)
- **Frontend**: React 18.2 con interfaz moderna
- **Autenticación**: JWT con sistema de usuarios

### 1.2 Estado Actual del Proyecto

**Versión**: 2.2.0

**Estado**: ✅ Producción Ready

**Tareas Completadas**:

- ✅ Correcciones críticas (configuración Pydantic, API Redis Queue)
- ✅ Sistema de métricas y monitoreo
- ✅ Manejo de errores mejorado
- ✅ Optimización de queries de base de datos
- ✅ Documentación consolidada

**Tareas en Progreso**:

- 🔄 Consolidación de modelos de base de datos
- 🔄 Migración de `config.py` a `environment.py` (10 archivos pendientes)
- 🔄 Migración completa de routes legacy a API v2
- 🔄 Aumentar cobertura de tests a >80%

### 1.3 Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React)                        │
│                   http://localhost:3001                      │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│              FastAPI Application (Puerto 8006)               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   API v1     │  │   API v2      │  │   Auth       │     │
│  │  (Legacy)    │  │  (Current)    │  │   JWT        │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Services Layer                          │   │
│  │  • OptimalOCRService (Tesseract/Google/AWS)         │   │
│  │  • IntelligentExtractionService (LLM + NLP)         │   │
│  │  • AFIPInvoiceExtractionService                     │   │
│  │  • AcademicDocumentExtractionService                │   │
│  │  • DNIExtractionService                             │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Repository Layer                         │   │
│  │  • DocumentRepository                                │   │
│  └──────────────────────────────────────────────────────┘   │
└───────────────┬───────────────────────┬─────────────────────┘
                │                       │
    ┌───────────▼──────────┐  ┌────────▼──────────┐
    │   PostgreSQL (5434)   │  │  Redis (6380)     │
    │   Base de Datos       │  │  Cache + Queue    │
    └───────────────────────┘  └───────────────────┘
                │
    ┌───────────▼──────────┐
    │   Worker (RQ)        │
    │   Procesamiento      │
    │   Asíncrono          │
    └──────────────────────┘
```

## 2. Setup Inicial

### 2.1 Requisitos Previos

- Python 3.13
- Docker y Docker Compose
- Git
- Editor de código (VS Code recomendado)

### 2.2 Opción 1: Setup con Docker (Recomendado)

```bash
# 1. Clonar repositorio (si no lo tienes)
git clone <repo-url>
cd invoice-data-simple-AI

# 2. Construir e iniciar todos los servicios
docker-compose up -d

# 3. Verificar que todo funciona
curl http://localhost:8006/health

# 4. Acceder a servicios
# - API Docs: http://localhost:8006/docs
# - Frontend: http://localhost:3001
# - PostgreSQL: localhost:5434
# - Redis: localhost:6380
# - PgAdmin: http://localhost:5050 (con profile dev)
```

### 2.3 Opción 2: Setup Local

```bash
# 1. Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Instalar modelo de spaCy
python -m spacy download es_core_news_sm

# 4. Configurar variables de entorno
cp env.example .env
# Editar .env con tus configuraciones

# 5. Inicializar base de datos
alembic upgrade head

# 6. Crear usuario admin (opcional)
python create_admin_user.py

# 7. Iniciar servidor
python main.py
```

### 2.4 Configuración Mínima (Sin APIs Externas)

Para empezar sin configurar APIs externas:

```env
# .env
DATABASE_URL=sqlite:///./data/documents.db
# Dejar vacío REDIS_URL para deshabilitar cache
# Dejar vacías todas las API keys (solo Tesseract + spaCy)
```

### 2.5 Configuración con Servicios Gratuitos

Si quieres usar servicios gratuitos para empezar:

```env
# Base de datos: Supabase (500MB gratis)
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROYECTO].supabase.co:5432/postgres

# Redis: Upstash (10k requests/día gratis)
REDIS_URL=rediss://:[PASSWORD]@[HOST].upstash.io:6380

# Google Vision: 1000 requests/mes gratis
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json

# OpenAI: $5 USD gratis para nuevas cuentas
OPENAI_API_KEY=sk-...
```

## 3. Estructura del Proyecto

### 3.1 Directorios Principales

```
invoice-data-simple-AI/
├── src/app/                    # Código fuente principal
│   ├── main.py                # Aplicación FastAPI
│   ├── core/                  # Configuración y base de datos
│   │   ├── config.py          # Config legacy (deprecar)
│   │   ├── environment.py     # Config nueva (usar)
│   │   └── database.py        # Conexión BD
│   ├── models/                # Modelos SQLAlchemy
│   ├── schemas/               # Esquemas Pydantic v2
│   ├── services/              # Lógica de negocio (14 servicios)
│   ├── repositories/          # Capa de acceso a datos
│   ├── api/                   # Endpoints organizados
│   │   ├── v1/                # API Legacy
│   │   └── v2/                # API Actual
│   ├── routes/                # Routes legacy (deprecar)
│   ├── auth/                  # Autenticación JWT
│   └── middleware/            # Middleware personalizado
├── frontend/                  # Aplicación React
├── tests/                     # Tests automatizados
│   ├── unit/                  # Tests unitarios
│   ├── integration/           # Tests de integración
│   └── e2e/                   # Tests end-to-end
├── alembic/                   # Migraciones de BD
├── docs/                      # Documentación técnica
└── docker-compose.yml         # Configuración Docker
```

### 3.2 Servicios Clave

**OCR Services**:

- `OptimalOCRService`: Selección automática del mejor OCR
- `SpecializedOCRService`: OCR con preprocesamiento avanzado

**Extraction Services**:

- `BasicExtractionService`: Regex + spaCy básico
- `IntelligentExtractionService`: LLM + NLP avanzado
- `AFIPInvoiceExtractionService`: Especializado en facturas AFIP
- `AcademicDocumentExtractionService`: Documentos académicos
- `DNIExtractionService`: DNI argentinos

**Validation Services**:

- `UniversalValidationService`: Validación genérica
- `AFIPValidationService`: Validación CAE AFIP

## 4. Flujo de Desarrollo

### 4.1 Workflow Diario

```bash
# 1. Activar entorno virtual
.venv\Scripts\activate

# 2. Iniciar servicios Docker (si usas Docker)
docker-compose up -d

# 3. Iniciar servidor con hot-reload
python main.py
# O con uvicorn directamente
uvicorn app.main:app --reload --port 8005

# 4. Ejecutar tests
pytest tests/ -v

# 5. Ver logs
tail -f logs/app.log
```

### 4.2 Agregar Nueva Funcionalidad

#### 4.2.1 Agregar Nuevo Endpoint

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

Luego registrar en `src/app/api/v2/__init__.py`:

```python
from .nuevo_endpoint import router as nuevo_router
api_router.include_router(nuevo_router, tags=["Nuevo"])
```

#### 4.2.2 Agregar Nuevo Servicio

```python
# En src/app/services/nuevo_servicio.py
class NuevoServicio:
    def __init__(self):
        pass
    
    def procesar(self, data):
        # Lógica aquí
        return resultado
```

#### 4.2.3 Agregar Nuevo Modelo

```python
# En src/app/models/nuevo_modelo.py
from ..core.database import Base
from sqlalchemy import Column, Integer, String

class NuevoModelo(Base):
    __tablename__ = "nuevo_modelo"
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(255))
```

Crear migración:

```bash
alembic revision --autogenerate -m "add_nuevo_modelo"
alembic upgrade head
```

### 4.3 Testing

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
pytest tests/unit/test_improved_precision.py -v

# Con reporte detallado
pytest tests/ -v --tb=short
```

### 4.4 Migraciones de Base de Datos

```bash
# Ver estado actual
alembic current

# Ver historial
alembic history --verbose

# Crear nueva migración
alembic revision --autogenerate -m "descripcion_cambio"

# Aplicar migraciones
alembic upgrade head

# Revertir última migración
alembic downgrade -1
```

## 5. Endpoints y API

### 5.1 API v2 (Recomendada)

**Documentos**:
- `GET /api/v2/documents/` - Listar documentos con filtros
- `POST /api/v2/documents/` - Crear documento
- `GET /api/v2/documents/{id}` - Obtener documento
- `PUT /api/v2/documents/{id}` - Actualizar documento
- `DELETE /api/v2/documents/{id}` - Eliminar documento
- `POST /api/v2/documents/search` - Búsqueda avanzada
- `POST /api/v2/documents/{id}/process` - Procesar documento

**Uploads**:
- `POST /api/v2/uploads/` - Subir archivo

**Analytics**:
- `GET /api/v2/analytics/overview` - Estadísticas generales

### 5.2 API v1 (Legacy - Mantenimiento)

- `POST /api/v1/upload` - Upload simple
- `POST /api/v1/upload-flexible` - Upload con selección de métodos
- `GET /api/v1/documents` - Listar documentos
- `GET /api/v1/documents/{id}` - Obtener documento

### 5.3 Autenticación

- `POST /auth/register` - Registrar usuario
- `POST /auth/login` - Iniciar sesión
- `POST /auth/refresh` - Renovar token
- `GET /auth/me` - Usuario actual

### 5.4 Sistema

- `GET /health` - Health check
- `GET /info` - Información del sistema
- `GET /metrics` - Métricas del sistema

## 6. Tipos de Documentos Soportados

### 6.1 Documentos Comerciales

- **Facturas AFIP**: Con validación CAE
- **Recibos**: Recibos de pago
- **Boletas**: Boletas de venta
- **Notas**: Notas de débito/crédito

### 6.2 Documentos Académicos

- **Títulos**: Títulos universitarios
- **Certificados**: Certificados de cursos
- **Diplomas**: Diplomas de graduación
- **Licencias**: Licencias profesionales

### 6.3 Documentos de Identidad

- **DNI Tarjeta**: DNI argentino (tarjeta)
- **DNI Libreta**: DNI argentino (libreta)
- **Pasaportes**: Pasaportes argentinos
- **Licencias de Conducir**: Licencias de conducir

## 7. Procesamiento de Documentos

### 7.1 Flujo de Procesamiento

1. **Upload**: El usuario sube un documento (PDF, imagen)
2. **OCR**: El sistema extrae texto usando OCR híbrido
3. **Detección**: Se detecta automáticamente el tipo de documento
4. **Extracción**: Se extraen datos estructurados usando servicios especializados
5. **Validación**: Se validan los datos extraídos
6. **Almacenamiento**: Se guarda en la base de datos con metadatos

### 7.2 Métodos de OCR Disponibles

- **Tesseract**: Gratis, siempre disponible, buena precisión
- **Google Vision**: Alta precisión, límite diario configurable
- **AWS Textract**: Alta precisión, límite diario configurable
- **Auto**: Selección automática basada en complejidad y disponibilidad

### 7.3 Métodos de Extracción

- **Regex**: Extracción basada en patrones
- **spaCy**: Procesamiento de lenguaje natural
- **LLM (OpenAI)**: Extracción con inteligencia artificial
- **Híbrido**: Combinación de múltiples métodos

## 8. Troubleshooting

### 8.1 Problemas Comunes

**Error: "relation documents does not exist"**
```bash
# Aplicar migraciones
alembic upgrade head
```

**Error: "tesseract is not installed"**
- **Docker**: Ya incluido en la imagen
- **Local**: Instalar desde https://github.com/UB-Mannheim/tesseract/wiki

**Error: "spaCy model not found"**
```bash
python -m spacy download es_core_news_sm
```

**Error: "Redis connection failed"**
- El sistema funciona sin Redis, pero sin cache ni procesamiento asíncrono
- Verificar que Redis esté corriendo: `docker-compose ps redis`

**Error: "PostgreSQL connection failed"**
- El sistema hace fallback automático a SQLite
- Verificar credenciales en `.env`

### 8.2 Verificar Estado del Sistema

```bash
# Health check
curl http://localhost:8006/health

# Información del sistema
curl http://localhost:8006/info

# Métricas
curl http://localhost:8006/metrics
```

### 8.3 Logs

```bash
# Logs de la aplicación
tail -f logs/app.log

# Logs de errores
tail -f logs/error.log

# Logs del sistema
tail -f logs/system.log

# Logs de Docker
docker-compose logs -f app
```

## 9. Próximos Pasos y Mejoras

### 9.1 Tareas Prioritarias

1. **Consolidar Modelos de Base de Datos**
   - Migrar a modelos unificados
   - Ver guía: `docs/MODELOS_CONSOLIDACION.md`

2. **Migrar Configuración**
   - Completar migración de `config.py` a `environment.py`
   - Ver guía: `docs/CONFIG_CONSOLIDACION.md`

3. **Migrar Routes Legacy**
   - Completar migración a API v2
   - Ver guía: `docs/ROUTES_MIGRATION_GUIDE.md`

4. **Aumentar Cobertura de Tests**
   - Objetivo: >80%
   - Agregar tests para servicios faltantes

### 9.2 Mejoras Futuras

- Dashboard de métricas en tiempo real
- Soporte para más tipos de documentos
- Mejoras en precisión de OCR
- Optimización de rendimiento
- Internacionalización (i18n)
- Webhooks para notificaciones
- API GraphQL (opcional)

## 10. Buenas Prácticas

### 10.1 Desarrollo

- **Rutas finas**: Lógica en servicios, no en endpoints
- **Validación**: Usar Pydantic v2 para validación
- **Manejo de errores**: HTTPException con mensajes claros
- **Logging**: Usar logger en lugar de print
- **Tests**: Escribir tests al agregar features
- **Type hints**: Usar tipos en todas las funciones
- **Docstrings**: Documentar funciones públicas

### 10.2 Código

- Seguir PEP 8 para estilo de código
- Usar nombres descriptivos en inglés
- Organizar imports (stdlib, third-party, local)
- Mantener funciones pequeñas y enfocadas
- Evitar duplicación de código

### 10.3 Git

- Usar Conventional Commits:
  - `feat:` Nueva funcionalidad
  - `fix:` Corrección de bug
  - `docs:` Cambios en documentación
  - `test:` Agregar o modificar tests
  - `refactor:` Refactorización de código
  - `chore:` Tareas de mantenimiento

## 11. Recursos y Documentación

### 11.1 Documentación del Proyecto

- **README.md**: Guía principal
- **README_DEV.md**: Manual para desarrolladores
- **CHANGELOG.md**: Historial de cambios
- **docs/**: Documentación técnica detallada
- **tests/README.md**: Guía de testing

### 11.2 Documentación Externa

- **FastAPI**: https://fastapi.tiangolo.com/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **Pydantic v2**: https://docs.pydantic.dev/
- **Alembic**: https://alembic.sqlalchemy.org/
- **React**: https://react.dev/

### 11.3 Guías Específicas

- **Migraciones**: `GUIA-MIGRACIONES.md`
- **Consolidación de Modelos**: `docs/MODELOS_CONSOLIDACION.md`
- **Consolidación de Config**: `docs/CONFIG_CONSOLIDACION.md`
- **Migración de Routes**: `docs/ROUTES_MIGRATION_GUIDE.md`

## 12. Ejemplos de Uso

### 12.1 Subir y Procesar Documento

```bash
# Subir documento
curl -X POST "http://localhost:8006/api/v2/uploads/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@factura.pdf" \
  -F "document_type=factura"

# Procesar documento
curl -X POST "http://localhost:8006/api/v2/documents/1/process" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 12.2 Buscar Documentos

```bash
# Búsqueda simple
curl "http://localhost:8006/api/v2/documents/?search=factura"

# Búsqueda avanzada
curl -X POST "http://localhost:8006/api/v2/documents/search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "query": "factura",
    "filters": {
      "document_type": "factura",
      "date_from": "2024-01-01"
    }
  }'
```

### 12.3 Obtener Estadísticas

```bash
curl "http://localhost:8006/api/v2/analytics/overview" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 13. Despliegue en Producción

### 13.1 Con Docker Compose

```bash
# Usar configuración de producción
docker-compose -f docker-compose.prod.yml up -d

# Con Nginx y SSL
docker-compose -f docker-compose.prod.yml --profile production up -d
```

### 13.2 Variables de Entorno para Producción

Asegúrate de configurar:
- `SECRET_KEY` seguro y único
- `DATABASE_URL` con credenciales de producción
- `DEBUG=False`
- `ENVIRONMENT=production`
- `CORS_ORIGINS` con dominios específicos
- `TRUSTED_HOSTS` configurado

### 13.3 Checklist de Producción

- [ ] Variables de entorno configuradas
- [ ] Base de datos de producción configurada
- [ ] Redis configurado (opcional pero recomendado)
- [ ] SSL/TLS configurado
- [ ] CORS configurado correctamente
- [ ] Rate limiting habilitado
- [ ] Logging configurado
- [ ] Monitoreo configurado
- [ ] Backups configurados
- [ ] Tests pasando

## 14. Contribuir al Proyecto

### 14.1 Proceso de Contribución

1. **Fork el proyecto** en GitHub
2. **Crear una rama** para tu feature:
   ```bash
   git checkout -b feature/nueva-funcionalidad
   ```
3. **Hacer cambios** siguiendo las buenas prácticas
4. **Escribir tests** para nuevas funcionalidades
5. **Commit con mensajes claros**:
   ```bash
   git commit -m 'feat: agregar nueva funcionalidad X'
   ```
6. **Push a tu fork**:
   ```bash
   git push origin feature/nueva-funcionalidad
   ```
7. **Abrir Pull Request** en GitHub con descripción clara

### 14.2 Estándares de Código

- Todos los tests deben pasar
- Cobertura de código debe mantenerse o aumentar
- El código debe seguir PEP 8
- Documentar funciones públicas
- Agregar ejemplos cuando sea apropiado

---

**Versión del Tutorial**: 1.0  
**Última Actualización**: Diciembre 2024  
**Proyecto**: Document Extractor API v2.2.0

Para más información, consulta la documentación en `docs/` o visita la documentación interactiva en `http://localhost:8006/docs` cuando el servidor esté corriendo.


