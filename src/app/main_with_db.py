"""
FastAPI App con conexión a base de datos SQLite
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
import sys

# Configurar SQLite
os.environ["DATABASE_URL"] = "sqlite:///./data/documents.db"

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from .core.config import settings
from .core.database import engine, Base, get_db
from .routes import documents_enhanced_db
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
    title="Document Extractor API - Enhanced with Database",
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

# Middleware para CORS headers
@app.middleware("http")
async def add_cors_headers(request, call_next):
    resp = await call_next(request)
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "*"
    return resp

# Incluir rutas mejoradas (v2)
app.include_router(documents_enhanced_db.router, prefix="/api/v2", tags=["Documents Enhanced"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to the OCR Document Processor API!",
        "version": "2.0.0",
        "status": "Enhanced Mode with Database",
        "database": "SQLite",
        "features": [
            "Pydantic v2 Schemas",
            "Enhanced Document Processing",
            "Advanced Search",
            "Batch Operations",
            "Export Functionality",
            "Statistics Dashboard",
            "Database Integration"
        ],
        "endpoints": {
            "v2_documents": "/api/v2/documents/",
            "v2_search": "/api/v2/documents/search",
            "v2_stats": "/api/v2/documents/stats/overview",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "database": "SQLite",
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.get("/database/info")
async def database_info(db: Session = Depends(get_db)):
    """Información de la base de datos"""
    try:
        # Verificar conexión
        db.execute("SELECT 1")
        
        # Obtener información de tablas
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        return {
            "status": "connected",
            "database_type": "SQLite",
            "tables": tables,
            "total_tables": len(tables)
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@app.get("/database/tables")
async def list_tables():
    """Listar todas las tablas de la base de datos"""
    try:
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        table_info = {}
        for table in tables:
            columns = inspector.get_columns(table)
            table_info[table] = {
                "columns": [col["name"] for col in columns],
                "column_count": len(columns)
            }
        
        return {
            "tables": table_info,
            "total_tables": len(tables)
        }
    except Exception as e:
        return {
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
