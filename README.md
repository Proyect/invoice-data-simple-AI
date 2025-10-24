# Document Extractor API

API optimizada para extraer datos de documentos usando **OCR híbrido**, **LLMs** y **procesamiento asíncrono**.

## 🚀 Inicio Rápido

### Opción 1: Docker (Recomendado)

```bash
# 1. Construir e iniciar
docker-compose up -d

# 2. Verificar
curl http://localhost:8006/health

# 3. Documentación
http://localhost:8006/docs
```

### Opción 2: Local

```bash
# 1. Activar entorno virtual
.venv\Scripts\activate

# 2. Iniciar servidor
python start.py

# 3. Documentación
http://localhost:8005/docs
```

## 📋 Características

- **OCR Híbrido**: Tesseract (gratis) + Google Vision + AWS Textract
- **Extracción Inteligente**: Regex + spaCy + OpenAI GPT
- **Base de Datos**: PostgreSQL + SQLite fallback
- **Procesamiento Asíncrono**: Redis Queue + Workers
- **Docker**: Despliegue completo incluido

## 🔧 Configuración

### Variables de Entorno (.env)

```env
# Base
APP_NAME=Document Extractor API
DEBUG=True
PORT=8005

# Base de datos
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/document_extractor

# APIs Opcionales
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

## 📊 Endpoints Principales

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/v1/upload` | POST | Upload simple (Tesseract + spaCy) |
| `/api/v1/upload-flexible` | POST | Upload con selección de métodos |
| `/api/v1/documents` | GET | Listar documentos |
| `/api/v1/documents/{id}` | GET | Obtener documento |
| `/health` | GET | Health check |
| `/docs` | GET | Documentación Swagger |

## 🧪 Pruebas

### Tests Automatizados
```bash
# Ejecutar todos los tests
python run_tests.py

# Tests con modo verbose
python run_tests.py --verbose

# Solo tests unitarios
python run_tests.py --type unit

# Con cobertura de código
python run_tests.py --coverage
```

### Tests de Producción
```bash
# Test del sistema de producción
python tests/test_production_system.py

# Test detallado de endpoints
python tests/test_production_system.py --detailed
```

### Health Check
```bash
curl http://localhost:8005/health
```

### Subir Documento
```bash
curl -X POST "http://localhost:8005/api/v2/uploads/" \
  -F "file=@documento.pdf" \
  -F "document_type=factura"
```

### Verificar Sistema
```bash
curl http://localhost:8005/info
```

## 🐳 Docker

### Servicios Incluidos
- **app**: API principal (puerto 8006)
- **postgres**: Base de datos (puerto 5434)
- **redis**: Cache y colas (puerto 6380)
- **worker**: Procesamiento asíncrono
- **pgadmin**: Admin DB (puerto 5050)

### Comandos Útiles
```bash
# Ver logs
docker-compose logs -f app

# Reiniciar
docker-compose restart

# Detener
docker-compose down
```

## 🔍 Troubleshooting

### Error: "relation documents does not exist"
```bash
# Ejecutar migración
alembic upgrade head
```

### Error: "tesseract is not installed"
- **Docker**: Ya incluido
- **Local**: Instalar desde https://github.com/UB-Mannheim/tesseract/wiki

### Error: "spaCy model not found"
```bash
python -m spacy download es_core_news_sm
```

## 📁 Estructura del Proyecto

```
src/app/
├── main.py              # Aplicación FastAPI
├── core/                # Configuración y DB
├── models/              # Modelos SQLAlchemy
├── routes/              # Endpoints API
├── services/            # Lógica de negocio
└── schemas/             # Esquemas Pydantic
```

## 🚀 Despliegue en Producción

```bash
# Usar configuración de producción
docker-compose -f docker-compose.prod.yml up -d

# Con Nginx y SSL
docker-compose -f docker-compose.prod.yml --profile production up -d
```

## 📄 Licencia

MIT License

## 🤝 Contribuir

1. Fork el proyecto
2. Crear rama: `git checkout -b feature/nueva-funcionalidad`
3. Commit: `git commit -m 'Agregar nueva funcionalidad'`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Abrir Pull Request

---

**¡Listo para extraer datos de documentos! 🎉**