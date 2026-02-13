# Document Extractor API

Sistema profesional de extracción y análisis de documentos con IA, OCR híbrido y procesamiento asíncrono.

## 🚀 Inicio Rápido

### Opción 1: Docker (Recomendado)

```bash
# 1. Construir e iniciar todos los servicios
docker-compose up -d

# 2. Verificar que todo funciona
curl http://localhost:8006/health

# 3. Acceder a la documentación
# API Docs: http://localhost:8006/docs
# Frontend: http://localhost:3001
```

### Opción 2: Instalación Local

```bash
# 1. Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
cp env.example .env
# Editar .env con tus configuraciones

# 4. Iniciar servidor
python main.py

# 5. Acceder a la documentación
# http://localhost:8005/docs
```

## 📋 Características Principales

- **OCR Híbrido**: Tesseract (gratis) + Google Vision + AWS Textract
- **Extracción Inteligente**: Regex + spaCy + OpenAI GPT
- **Base de Datos**: PostgreSQL (producción) / SQLite (desarrollo/fallback)
- **Procesamiento Asíncrono**: Redis Queue + Workers
- **Autenticación JWT**: Sistema seguro de usuarios
- **API RESTful**: Endpoints v1 (legacy) y v2 (actual)
- **Frontend React**: Interfaz web moderna
- **Docker**: Despliegue completo incluido

## 🔧 Configuración

### Variables de Entorno Esenciales

Crea un archivo `.env` basado en `env.example`:

```env
# Aplicación
APP_NAME=Document Extractor API
DEBUG=True
PORT=8005
HOST=0.0.0.0

# Base de Datos
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/document_extractor
DATABASE_URL_FALLBACK=sqlite:///./data/documents.db

# Redis (opcional)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Seguridad
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# APIs Opcionales (para funcionalidades avanzadas)
OPENAI_API_KEY=sk-...                    # Para extracción con LLM
GOOGLE_APPLICATION_CREDENTIALS=...       # Para Google Vision OCR
AWS_ACCESS_KEY_ID=...                    # Para AWS Textract
AWS_SECRET_ACCESS_KEY=...
```

### Obtener API Keys

#### OpenAI GPT (Recomendado para empezar)
1. Ir a https://platform.openai.com/api-keys
2. Crear nueva API key
3. Agregar a `.env`: `OPENAI_API_KEY=sk-...`

#### Google Cloud Vision (Opcional)
1. Ir a https://console.cloud.google.com/
2. Crear proyecto y habilitar Vision API
3. Crear Service Account y descargar JSON
4. Agregar a `.env`: `GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json`

## 🌐 Acceso al Sistema

Una vez iniciado, puedes acceder de varias formas:

### 1. Interfaz Web (Frontend React)
```
URL: http://localhost:3001
```
- Interfaz gráfica para subir y gestionar documentos
- La forma más fácil de usar el sistema

### 2. Documentación Interactiva (Swagger UI)
```
URL: http://localhost:8006/docs
```
- Interfaz interactiva para probar todos los endpoints
- Ideal para desarrolladores
- Puedes probar subir documentos directamente desde aquí

### 3. API REST Directa
```
Base URL: http://localhost:8006
```

**Ejemplo con cURL:**
```bash
# Health check
curl http://localhost:8006/health

# Subir documento
curl -X POST "http://localhost:8006/api/v1/upload" \
  -F "file=@documento.pdf" \
  -F "document_type=factura"

# Listar documentos
curl http://localhost:8006/api/v1/documents
```

### 4. Base de Datos
```
PostgreSQL: localhost:5434
Redis: localhost:6380
```

## 📊 Endpoints Principales

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/health` | GET | Health check del sistema |
| `/info` | GET | Información del sistema |
| `/api/v1/upload` | POST | Upload simple (Tesseract + spaCy) |
| `/api/v1/upload-flexible` | POST | Upload con selección de métodos |
| `/api/v1/documents` | GET | Listar documentos |
| `/api/v1/documents/{id}` | GET | Obtener documento |
| `/api/v2/documents/` | GET | Listar documentos (v2) |
| `/api/v2/documents/{id}` | GET | Obtener documento (v2) |
| `/api/v2/documents/search` | POST | Búsqueda avanzada |
| `/api/v2/documents/{id}/process` | POST | Procesar documento |
| `/auth/login` | POST | Iniciar sesión |
| `/auth/register` | POST | Registrar usuario |
| `/docs` | GET | Documentación Swagger |

Para ver todos los endpoints disponibles, visita `/docs` cuando el servidor esté corriendo.

## 🐳 Docker

### Servicios Incluidos

- **app**: API principal (puerto 8006)
- **postgres**: Base de datos (puerto 5434)
- **redis**: Cache y colas (puerto 6380)
- **worker**: Procesamiento asíncrono
- **frontend**: Interfaz web React (puerto 3001)
- **pgadmin**: Admin DB (puerto 5050, solo con profile dev)

### Comandos Útiles

```bash
# Ver logs
docker-compose logs -f app

# Reiniciar servicios
docker-compose restart

# Detener servicios
docker-compose down

# Ver estado de servicios
docker-compose ps

# Ejecutar migraciones
docker-compose exec app alembic upgrade head
```

## 🧪 Pruebas

```bash
# Ejecutar todos los tests
python run_tests.py

# Tests con modo verbose
python run_tests.py --verbose

# Solo tests unitarios
python run_tests.py --type unit

# Con cobertura de código
python run_tests.py --coverage

# O directamente con pytest
pytest tests/ --cov=src/app --cov-report=html --cov-report=term

# Ejecutar tests por categoría
pytest tests/unit/          # Tests unitarios
pytest tests/integration/   # Tests de integración
pytest tests/e2e/           # Tests end-to-end
```

**Nota**: Para generar reportes de cobertura, asegúrate de tener `pytest-cov` instalado:
```bash
pip install pytest-cov
```

## 🔍 Troubleshooting

### Error: "relation documents does not exist"
```bash
# Ejecutar migración
alembic upgrade head
```

### Error: "tesseract is not installed"
- **Docker**: Ya incluido en la imagen
- **Local**: Instalar desde https://github.com/UB-Mannheim/tesseract/wiki

### Error: "spaCy model not found"
```bash
# Instalar spaCy si no está instalado
pip install spacy

# Descargar modelo en español
python -m spacy download es_core_news_sm
```

**Nota**: spaCy está incluido en `requirements.txt`, pero el modelo de idioma debe descargarse por separado.

### Error: "Redis connection failed"
- El sistema funciona sin Redis, pero sin cache ni procesamiento asíncrono
- Verificar que Redis esté corriendo: `docker-compose ps redis`

### Error: "PostgreSQL connection failed"
- El sistema hace fallback automático a SQLite
- Verificar credenciales en `.env`

## 📁 Estructura del Proyecto

```
src/app/
├── main.py              # Aplicación FastAPI principal
├── core/                # Configuración y base de datos
│   ├── config.py        # Configuraciones
│   ├── database.py      # Conexión a BD
│   └── environment.py    # Gestión de ambientes
├── models/              # Modelos SQLAlchemy
├── schemas/             # Esquemas Pydantic v2
├── services/            # Lógica de negocio
│   ├── optimal_ocr_service.py
│   ├── intelligent_extraction_service.py
│   └── ...
├── routes/              # Endpoints (legacy)
├── api/                 # API v1 y v2
│   ├── v1/              # API Legacy
│   └── v2/              # API Actual
├── auth/                # Autenticación JWT
├── repositories/        # Capa de acceso a datos
└── middleware/          # Middleware personalizado

frontend/                # Aplicación React
tests/                   # Tests automatizados
alembic/                 # Migraciones de base de datos
```

## 🚀 Despliegue en Producción

### Con Docker Compose

```bash
# Usar configuración de producción
docker-compose -f docker-compose.prod.yml up -d

# Con Nginx y SSL
docker-compose -f docker-compose.prod.yml --profile production up -d
```

### Variables de Entorno para Producción

Asegúrate de configurar:
- `SECRET_KEY` seguro y único
- `DATABASE_URL` con credenciales de producción
- `DEBUG=False`
- `ENVIRONMENT=production`
- Configurar CORS con dominios específicos

## 📄 Tipos de Documentos Soportados

- **Comerciales**: Facturas AFIP, Recibos, Boletas, Notas
- **Académicos**: Títulos, Certificados, Diplomas, Licencias
- **Identidad**: DNI, Pasaportes, Licencias de conducir
- **Otros**: Contratos, Formularios

## 🤝 Contribuir

Para contribuir al proyecto, consulta la guía completa en [README_DEV.md](README_DEV.md#-contribución).

## 📚 Documentación Adicional

- **Desarrolladores**: Ver [README_DEV.md](README_DEV.md)
- **Tests**: Ver [tests/README.md](tests/README.md)
- **Migraciones**: Ver [GUIA-MIGRACIONES.md](GUIA-MIGRACIONES.md)
- **Documentación Técnica**: Ver [docs/README.md](docs/README.md)
  - Consolidación de Modelos
  - Consolidación de Configuración
  - Migración de Routes Legacy
  - Actualización de Dependencias
- **Cambios Recientes**: Ver [CHANGELOG.md](CHANGELOG.md)

## 📄 Licencia

MIT License

---

**Versión**: 2.1.0  
**Estado**: ✅ Producción Ready
