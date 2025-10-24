"""
FastAPI App simple con base de datos
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
from .models.document import Document
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
    title="Document Extractor API - Simple with Database",
    description="API simple con conexión a base de datos",
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

@app.get("/")
async def root():
    return {
        "message": "Welcome to the OCR Document Processor API!",
        "version": "2.0.0",
        "status": "Simple Mode with Database",
        "database": "SQLite"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "database": "SQLite"
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

# ============================================================================
# ENDPOINTS V2 SIMPLES CON BASE DE DATOS
# ============================================================================

@app.get("/api/v2/documents/", summary="Listar documentos")
async def list_documents(
    page: int = 1,
    size: int = 10,
    db: Session = Depends(get_db)
):
    """Listar documentos desde la base de datos"""
    try:
        # Consulta simple
        offset = (page - 1) * size
        total = db.query(Document).count()
        documents = db.query(Document).offset(offset).limit(size).all()
        
        return {
            "items": [
                {
                    "id": doc.id,
                    "filename": doc.filename,
                    "document_type": doc.document_type,
                    "status": doc.status,
                    "confidence_score": doc.confidence_score,
                    "created_at": doc.created_at.isoformat() if doc.created_at else None
                }
                for doc in documents
            ],
            "total": total,
            "page": page,
            "size": size,
            "total_pages": (total + size - 1) // size
        }
    except Exception as e:
        logger.error(f"Error listando documentos: {e}")
        return {
            "error": str(e),
            "items": [],
            "total": 0,
            "page": page,
            "size": size
        }

@app.post("/api/v2/documents/", summary="Crear documento")
async def create_document(
    filename: str,
    document_type: str = "factura",
    status: str = "pending",
    confidence_score: float = 0.0,
    db: Session = Depends(get_db)
):
    """Crear un nuevo documento"""
    try:
        document = Document(
            filename=filename,
            document_type=document_type,
            status=status,
            confidence_score=confidence_score
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        return {
            "id": document.id,
            "filename": document.filename,
            "document_type": document.document_type,
            "status": document.status,
            "confidence_score": document.confidence_score,
            "created_at": document.created_at.isoformat() if document.created_at else None
        }
    except Exception as e:
        logger.error(f"Error creando documento: {e}")
        db.rollback()
        return {"error": str(e)}

@app.get("/api/v2/documents/{document_id}", summary="Obtener documento")
async def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Obtener un documento específico"""
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        
        if not document:
            return {"error": "Documento no encontrado"}
        
        return {
            "id": document.id,
            "filename": document.filename,
            "document_type": document.document_type,
            "status": document.status,
            "confidence_score": document.confidence_score,
            "created_at": document.created_at.isoformat() if document.created_at else None
        }
    except Exception as e:
        logger.error(f"Error obteniendo documento: {e}")
        return {"error": str(e)}

@app.get("/api/v2/documents/stats/overview", summary="Estadísticas")
async def get_documents_stats(db: Session = Depends(get_db)):
    """Obtener estadísticas de documentos"""
    try:
        total_documents = db.query(Document).count()
        processed_documents = db.query(Document).filter(Document.status == "processed").count()
        pending_documents = db.query(Document).filter(Document.status == "pending").count()
        
        return {
            "total_documents": total_documents,
            "processed_documents": processed_documents,
            "pending_documents": pending_documents,
            "failed_documents": 0,
            "average_confidence": 0.0,
            "processing_time_avg": 0.0
        }
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
