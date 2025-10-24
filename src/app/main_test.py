"""
FastAPI App de Prueba - Solo con rutas v2
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import documents_enhanced_simple
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title="Document Extractor API - Enhanced Mode",
    description="API mejorada para procesamiento de documentos con Pydantic schemas",
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

# Incluir SOLO rutas v2
app.include_router(documents_enhanced_simple.router, prefix="/api/v2", tags=["Documents Enhanced"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to the OCR Document Processor API!",
        "version": "2.0.0",
        "status": "Enhanced Mode",
        "features": [
            "Pydantic v2 Schemas",
            "Enhanced Document Processing",
            "Advanced Search",
            "Batch Operations",
            "Export Functionality",
            "Statistics Dashboard"
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
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.get("/info")
async def info():
    """API information endpoint"""
    return {
        "name": "Document Extractor API",
        "version": "2.0.0",
        "description": "API mejorada para procesamiento de documentos",
        "features": [
            "Pydantic v2 validation",
            "Enhanced schemas",
            "Advanced search",
            "Batch processing",
            "Export functionality"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
