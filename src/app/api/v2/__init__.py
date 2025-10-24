"""
API v2 (Current)
================

API actual con todas las funcionalidades optimizadas.
"""
from fastapi import APIRouter

# Router principal de v2
api_router = APIRouter()

# Importar y registrar sub-routers
from .documents import router as documents_router
from .uploads import router as uploads_router
from .processing import router as processing_router
from .analytics import router as analytics_router
from .auth import router as auth_router

api_router.include_router(documents_router, prefix="/documents", tags=["Documents v2"])
api_router.include_router(uploads_router, prefix="/uploads", tags=["Uploads v2"])
api_router.include_router(processing_router, prefix="/processing", tags=["Processing v2"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["Analytics v2"])
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication v2"])
