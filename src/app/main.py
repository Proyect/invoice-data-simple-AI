from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routes import documents, optimized_upload, simple_upload, flexible_upload
from app.core.database import engine, Base
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear tablas de la base de datos
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Tablas de base de datos creadas correctamente")
except Exception as e:
    logger.error(f"Error creando tablas: {e}")

app = FastAPI(
    title=settings.APP_NAME,
    description="API optimizada para extraer datos de documentos usando OCR híbrido, LLMs y procesamiento asíncrono",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Responder preflight OPTIONS para rutas comunes (algunos servers lo requieren explícito)
from fastapi import Response

@app.options("/{full_path:path}")
async def preflight(full_path: str):
    # Responder con headers CORS explícitos
    resp = Response(content="OK")
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "*"
    return resp

# Incluir rutas
app.include_router(simple_upload.router, prefix="/api/v1", tags=["upload-simple"])
app.include_router(flexible_upload.router, prefix="/api/v1", tags=["upload-flexible"])
# NOTA: Los siguientes endpoints requieren Redis y APIs configuradas
# app.include_router(optimized_upload.router, prefix="/api/v1", tags=["upload-optimized"])
app.include_router(documents.router, prefix="/api/v1", tags=["documents"])

@app.get("/")
async def root():
    return {
        "message": "Document Extractor API - Flexible Mode",
        "version": "2.1.0",
        "port": settings.PORT,
        "status": "Funcionando",
        "endpoints": {
            "simple": {
                "url": "/api/v1/upload",
                "descripcion": "Upload simple (Tesseract + spaCy)",
                "metodos_fijos": True
            },
            "flexible": {
                "url": "/api/v1/upload-flexible",
                "descripcion": "Upload con selección de métodos",
                "permite_elegir": ["OCR", "Extracción"]
            },
            "metodos_disponibles": "/api/v1/upload-flexible/methods"
        },
        "documentacion": "/docs",
        "health_check": "/health",
        "test_ocr": "/api/v1/upload/test",
        "features": [
            "Múltiples métodos de OCR (Tesseract, Google Vision, AWS)",
            "Múltiples métodos de extracción (Regex, spaCy, LLM)",
            "Selección automática o manual",
            "Base de datos PostgreSQL/SQLite",
            "Procesamiento flexible"
        ]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "port": settings.PORT,
        "database": "PostgreSQL",
        "cache": "Redis",
        "processing": "Async"
    }

@app.get("/info")
async def get_info():
    """Información detallada del sistema"""
    return {
        "app_name": settings.APP_NAME,
        "version": "2.0.0",
        "debug": settings.DEBUG,
        "port": settings.PORT,
        "database_url": settings.DATABASE_URL.split("@")[1] if "@" in settings.DATABASE_URL else "configured",
        "redis_url": settings.REDIS_URL,
        "features": {
            "ocr_hybrid": True,
            "llm_extraction": bool(settings.OPENAI_API_KEY),
            "async_processing": True,
            "cache": True,
            "full_text_search": True
        },
        "limits": {
            "google_vision_daily": settings.GOOGLE_VISION_DAILY_LIMIT,
            "aws_textract_daily": settings.AWS_TEXTRACT_DAILY_LIMIT,
            "worker_timeout": settings.RQ_WORKER_TIMEOUT
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
