"""
FastAPI App Principal - Sistema Optimizado de Procesamiento de Documentos
========================================================================

Sistema profesional de extracción y análisis de documentos con:
- Arquitectura modular y escalable
- Configuración por ambientes
- Schemas Pydantic v2 optimizados
- Autenticación JWT robusta
- Base de datos multi-soporte (PostgreSQL/SQLite)
- OCR híbrido inteligente
- Procesamiento asíncrono optimizado
- Cache multi-nivel
- API RESTful completa
- Documentación automática

Versión: 2.1.0
Autor: Sistema AI Assistant Optimizado
"""

import os
import sys
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Agregar src al path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Imports del sistema
from .core.environment import get_settings, Environment
from .core.database import init_database, close_database
from .core.logging_config import setup_logging
from .api.v1 import api_router as v1_router
from .api.v2 import api_router as v2_router
from .middleware.error_handler import ErrorHandlerMiddleware
from .middleware.performance import PerformanceMiddleware
from .middleware.security import SecurityMiddleware

# Configurar logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Gestión del ciclo de vida de la aplicación
    """
    # Startup
    logger.info("🚀 Iniciando Document Extractor API...")
    
    try:
        # Inicializar base de datos
        await init_database()
        logger.info("✅ Base de datos inicializada")
        
        # Inicializar servicios
        await app.state.services.initialize()
        logger.info("✅ Servicios inicializados")
        
        # Inicializar cache
        await app.state.cache.initialize()
        logger.info("✅ Cache inicializado")
        
        logger.info("🎉 Aplicación iniciada correctamente")
        
    except Exception as e:
        logger.error(f"❌ Error durante el startup: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Cerrando aplicación...")
    
    try:
        # Cerrar conexiones de base de datos
        await close_database()
        logger.info("✅ Conexiones de base de datos cerradas")
        
        # Cerrar servicios
        await app.state.services.cleanup()
        logger.info("✅ Servicios cerrados")
        
        # Cerrar cache
        await app.state.cache.cleanup()
        logger.info("✅ Cache cerrado")
        
        logger.info("✅ Aplicación cerrada correctamente")
        
    except Exception as e:
        logger.error(f"❌ Error durante el shutdown: {e}")


def create_app(environment: Environment = None) -> FastAPI:
    """
    Factory para crear la aplicación FastAPI
    """
    settings = get_settings()
    env = environment or settings.environment
    
    # Configurar aplicación
    app = FastAPI(
        title=settings.name,
        version=settings.version,
        description="Sistema profesional de extracción y análisis de documentos con IA",
        docs_url="/docs" if env != Environment.PRODUCTION else None,
        redoc_url="/redoc" if env != Environment.PRODUCTION else None,
        openapi_url="/openapi.json" if env != Environment.PRODUCTION else None,
        lifespan=lifespan,
    )
    
    # Configurar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if env == Environment.DEVELOPMENT else ["https://yourdomain.com"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Middleware de seguridad
    if env == Environment.PRODUCTION:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=["yourdomain.com"])
        app.add_middleware(SecurityMiddleware)
    
    # Middleware personalizado
    app.add_middleware(ErrorHandlerMiddleware)
    app.add_middleware(PerformanceMiddleware)
    
    # Incluir routers
    app.include_router(v1_router, prefix="/api/v1", tags=["API v1 (Legacy)"])
    app.include_router(v2_router, prefix="/api/v2", tags=["API v2 (Current)"])
    
    # Endpoints de salud y sistema
    @app.get("/", tags=["System"])
    async def root():
        """Endpoint raíz con información del sistema"""
        return {
            "name": settings.name,
            "version": settings.version,
            "environment": env.value,
            "status": "healthy",
            "docs": "/docs" if env != Environment.PRODUCTION else "disabled",
        }
    
    @app.get("/health", tags=["System"])
    async def health_check():
        """Health check detallado"""
        try:
            # Verificar base de datos
            db_status = await check_database_health()
            
            # Verificar servicios
            services_status = await check_services_health()
            
            # Verificar cache
            cache_status = await check_cache_health()
            
            overall_status = "healthy" if all([
                db_status["status"] == "healthy",
                services_status["status"] == "healthy",
                cache_status["status"] == "healthy"
            ]) else "degraded"
            
            return {
                "status": overall_status,
                "timestamp": "2024-01-01T00:00:00Z",  # TODO: usar datetime real
                "version": settings.version,
                "environment": env.value,
                "components": {
                    "database": db_status,
                    "services": services_status,
                    "cache": cache_status,
                }
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": "2024-01-01T00:00:00Z",
                }
            )
    
    @app.get("/info", tags=["System"])
    async def system_info():
        """Información detallada del sistema"""
        return {
            "application": {
                "name": settings.name,
                "version": settings.version,
                "environment": env.value,
                "debug": settings.debug,
            },
            "server": {
                "host": settings.host,
                "port": settings.port,
            },
            "features": {
                "ocr_providers": ["tesseract", "google_vision", "aws_textract"],
                "llm_providers": ["openai"],
                "databases": ["postgresql", "sqlite"],
                "cache": "redis",
                "async_processing": True,
            },
            "limits": {
                "max_file_size": "10MB",
                "supported_formats": ["pdf", "png", "jpg", "jpeg", "tiff"],
                "daily_ocr_limit": settings.ocr.google_vision_daily_limit,
            }
        }
    
    return app


async def check_database_health() -> dict:
    """Verificar salud de la base de datos"""
    try:
        # TODO: Implementar verificación real de BD
        return {"status": "healthy", "response_time_ms": 5}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


async def check_services_health() -> dict:
    """Verificar salud de los servicios"""
    try:
        # TODO: Implementar verificación real de servicios
        return {"status": "healthy", "services": ["ocr", "extraction", "llm"]}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


async def check_cache_health() -> dict:
    """Verificar salud del cache"""
    try:
        # TODO: Implementar verificación real de cache
        return {"status": "healthy", "type": "redis"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


# Crear aplicación por defecto
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    
    print(f"🚀 Iniciando {settings.name} v{settings.version}")
    print(f"🌍 Ambiente: {settings.environment.value}")
    print(f"🔗 Servidor: http://{settings.host}:{settings.port}")
    print(f"📖 Documentación: http://{settings.host}:{settings.port}/docs")
    print(f"🔍 Health check: http://{settings.host}:{settings.port}/health")
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if settings.debug else "warning",
        access_log=settings.debug,
    )