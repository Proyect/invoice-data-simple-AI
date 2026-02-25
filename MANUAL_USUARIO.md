# Manual del usuario — Document Extractor API

Sistema de extracción y análisis de documentos con IA, OCR híbrido y procesamiento asíncrono.

---

## Inicio rápido

### Con Docker (recomendado)

```bash
docker-compose up -d
curl http://localhost:8006/health
```

- **API**: http://localhost:8006  
- **Documentación interactiva**: http://localhost:8006/docs  
- **Frontend**: http://localhost:3001  

### Instalación local

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate   # Linux/Mac
pip install -r requirements.txt
cp env.example .env
# Editar .env con tu configuración
python main.py
```

- **API**: http://localhost:8005 (o el `PORT` de tu `.env`)  
- **Docs**: http://localhost:8005/docs  

---

## Características

- **OCR**: Tesseract, Google Vision, AWS Textract  
- **Extracción**: Regex, spaCy, OpenAI GPT  
- **Base de datos**: PostgreSQL (producción) o SQLite (desarrollo)  
- **Procesamiento asíncrono**: Redis + workers  
- **Autenticación**: JWT  
- **API**: REST v1 (legacy) y v2 (actual)  
- **Frontend**: Interfaz web React  

---

## Configuración mínima

Archivo `.env` (a partir de `env.example`):

```env
APP_NAME=Document Extractor API
DEBUG=True
PORT=8005
HOST=0.0.0.0

DATABASE_URL=postgresql://usuario:clave@localhost:5432/document_extractor
DATABASE_URL_FALLBACK=sqlite:///./data/documents.db

REDIS_HOST=localhost
REDIS_PORT=6379

SECRET_KEY=clave-secreta-segura-cambiar-en-produccion
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Producción**: Debes definir `SECRET_KEY` distinto del valor por defecto y usar `ENVIRONMENT=production`. Si no, la aplicación no arrancará.

### APIs opcionales

- **OpenAI**: `OPENAI_API_KEY=sk-...` (extracción con LLM)  
- **Google Vision**: `GOOGLE_APPLICATION_CREDENTIALS=/ruta/al/json`  
- **AWS Textract**: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, región  

---

## Uso del sistema

### 1. Interfaz web (React)

- URL: http://localhost:3001  
- Subir y gestionar documentos desde el navegador.  

### 2. Documentación interactiva (Swagger)

- URL: http://localhost:8006/docs (o el puerto que uses)  
- Probar todos los endpoints y subir archivos desde el navegador.  

### 3. API REST (ejemplos con curl)

```bash
# Estado del sistema
curl http://localhost:8006/health

# Subir documento
curl -X POST "http://localhost:8006/api/v1/upload" \
  -F "file=@documento.pdf" \
  -F "document_type=factura"

# Listar documentos
curl http://localhost:8006/api/v2/documents/
```

---

## Endpoints principales

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/health` | GET | Estado del sistema |
| `/info` | GET | Información y capacidades |
| `/metrics` | GET | Métricas (si está habilitado) |
| `/api/v1/upload` | POST | Subir archivo (legacy) |
| `/api/v2/uploads/` | POST | Subir archivo (v2) |
| `/api/v2/documents/` | GET | Listar documentos |
| `/api/v2/documents/{id}` | GET | Ver documento |
| `/api/v2/documents/search` | POST | Búsqueda avanzada |
| `/api/v2/documents/{id}/process` | POST | Procesar documento |
| `/api/v2/auth/login` | POST | Iniciar sesión |
| `/api/v2/auth/register` | POST | Registro |
| `/docs` | GET | Swagger UI |

La lista completa y los parámetros están en `/docs` con el servidor en marcha.

---

## Docker

### Servicios

- **app**: API (puerto 8006)  
- **postgres**: Base de datos (5434)  
- **redis**: Cache y colas (6380)  
- **worker**: Procesamiento asíncrono  
- **frontend**: Interfaz web (3001)  

### Comandos útiles

```bash
docker-compose logs -f app
docker-compose restart
docker-compose down
docker-compose ps
docker-compose exec app alembic upgrade head
```

---

## Tipos de documento soportados

- **Comerciales**: Facturas AFIP, recibos, boletas, notas  
- **Académicos**: Títulos, certificados, diplomas  
- **Identidad**: DNI, pasaportes, licencias  
- **Otros**: Contratos, formularios  

---

## Solución de problemas

- **"relation documents does not exist"**  
  Ejecutar migraciones: `alembic upgrade head` (o `docker-compose exec app alembic upgrade head`).

- **Tesseract no instalado**  
  En Docker ya viene en la imagen. En local: instalar desde la web de Tesseract.

- **Modelo spaCy no encontrado**  
  `pip install spacy` y `python -m spacy download es_core_news_sm`.

- **Redis no conecta**  
  La app sigue funcionando sin Redis (sin cache ni colas). Comprobar: `docker-compose ps redis`.

- **PostgreSQL no conecta**  
  Hay fallback a SQLite; revisar `DATABASE_URL` en `.env`.

---

Para desarrollo y contribución, ver **MANUAL_DESARROLLADOR.md**.
