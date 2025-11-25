"""
API v1 (Legacy)
===============

API legacy para compatibilidad con versiones anteriores.
"""
from fastapi import APIRouter

# Router principal de v1
api_router = APIRouter()

# Importar y registrar sub-routers
from .documents import router as documents_router
from .uploads import router as uploads_router
from .health import router as health_router

api_router.include_router(documents_router, prefix="/documents", tags=["Documents v1"])
api_router.include_router(uploads_router, prefix="", tags=["Uploads v1"])  # Sin prefijo para que los endpoints sean /api/v1/upload directamente
api_router.include_router(health_router, prefix="/health", tags=["Health v1"])
