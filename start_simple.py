#!/usr/bin/env python3
"""
Servidor Simple de Document Extractor
====================================
Servidor básico sin configuración compleja para desarrollo local.
"""

import os
import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Configurar variables de entorno antes de importar
os.environ["DATABASE_URL"] = "sqlite:///./data/documents.db"
os.environ["DATABASE_URL_TEST"] = "sqlite:///./data/documents_test.db"
os.environ["SECRET_KEY"] = "local-development-key-change-in-production-32-chars"
os.environ["DEBUG"] = "True"
os.environ["HOST"] = "0.0.0.0"
os.environ["PORT"] = "8005"

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Crear aplicación FastAPI simple
app = FastAPI(
    title="Document Extractor API - Simple",
    description="API simple para extracción de documentos",
    version="1.0.0"
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
    """Endpoint raíz"""
    return {
        "message": "Document Extractor API - Simple Mode",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "message": "API is running",
        "database": "sqlite (local)"
    }

@app.get("/docs")
async def docs():
    """Redirigir a la documentación"""
    return {"message": "Documentación disponible en /docs"}

if __name__ == "__main__":
    print("Iniciando Document Extractor API - Modo Simple")
    print("URL: http://localhost:8005")
    print("Documentacion: http://localhost:8005/docs")
    print("Health Check: http://localhost:8005/health")
    print("=" * 50)
    
    uvicorn.run(
        "start_simple:app",
        host="0.0.0.0",
        port=8005,
        reload=True,
        log_level="info"
    )
