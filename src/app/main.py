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
import time
from datetime import datetime, timezone
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
from .core.database import init_database, close_database, is_database_healthy, is_redis_healthy, get_redis
from .core.logging_config import setup_logging
from .api.v1 import api_router as v1_router
from .api.v2 import api_router as v2_router
from .middleware.error_handler import ErrorHandlerMiddleware
from .middleware.performance import PerformanceMiddleware
from .middleware.security import SecurityMiddleware
from .middleware.rate_limiting import RateLimitingMiddleware

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
        
        # Inicializar servicios (opcional)
        if hasattr(app.state, 'services'):
            try:
                await app.state.services.initialize()
                logger.info("✅ Servicios inicializados")
            except Exception as e:
                logger.warning(f"⚠️ Servicios no inicializados: {e}")
        else:
            logger.info("ℹ️ Servicios no configurados")
        
        # Inicializar cache (opcional)
        if hasattr(app.state, 'cache'):
            try:
                await app.state.cache.initialize()
                logger.info("✅ Cache inicializado")
            except Exception as e:
                logger.warning(f"⚠️ Cache no inicializado: {e}")
        else:
            logger.info("ℹ️ Cache no configurado")
        
        logger.info("🎉 Aplicación iniciada correctamente")
        
    except Exception as e:
        logger.error(f"❌ Error durante el startup: {e}")
        # No hacer raise para permitir que la app inicie aunque haya errores menores
        logger.warning("⚠️ Continuando con startup parcial...")
    
    yield
    
    # Shutdown
    logger.info("🛑 Cerrando aplicación...")
    
    try:
        # Cerrar conexiones de base de datos
        await close_database()
        logger.info("✅ Conexiones de base de datos cerradas")
        
        # Cerrar servicios (opcional)
        if hasattr(app.state, 'services'):
            try:
                await app.state.services.cleanup()
                logger.info("✅ Servicios cerrados")
            except Exception as e:
                logger.warning(f"⚠️ Error cerrando servicios: {e}")
        
        # Cerrar cache (opcional)
        if hasattr(app.state, 'cache'):
            try:
                await app.state.cache.cleanup()
                logger.info("✅ Cache cerrado")
            except Exception as e:
                logger.warning(f"⚠️ Error cerrando cache: {e}")
        
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
    cors_origins = settings.security.cors_origins
    if env == Environment.DEVELOPMENT and "*" not in cors_origins:
        # En desarrollo, permitir todos los orígenes por defecto
        cors_origins = ["*"]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=settings.security.cors_allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Middleware de seguridad
    if env == Environment.PRODUCTION:
        trusted_hosts = settings.security.trusted_hosts
        if trusted_hosts:
            app.add_middleware(TrustedHostMiddleware, allowed_hosts=trusted_hosts)
        app.add_middleware(SecurityMiddleware)
    
    # Rate Limiting Middleware
    if settings.security.rate_limit_enabled:
        app.add_middleware(
            RateLimitingMiddleware,
            requests_per_minute=settings.security.rate_limit_per_minute,
            burst=settings.security.rate_limit_burst,
            enabled=settings.security.rate_limit_enabled
        )
    
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
            
            # El sistema está healthy si la BD está healthy y los servicios principales están disponibles
            # Redis y algunos servicios OCR son opcionales
            overall_status = "healthy" if (
                db_status["status"] == "healthy" and 
                services_status["status"] in ["healthy", "degraded"]
            ) else "degraded"
            
            # Si Redis está unavailable pero BD está healthy, el sistema puede seguir funcionando
            if overall_status == "healthy" and cache_status["status"] == "unavailable":
                overall_status = "healthy"  # Redis es opcional
            
            return {
                "status": overall_status,
                "timestamp": datetime.now(timezone.utc).isoformat(),
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
                    "timestamp": datetime.now(timezone.utc).isoformat(),
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
        start_time = time.time()
        is_healthy = is_database_healthy()
        response_time_ms = int((time.time() - start_time) * 1000)
        
        if is_healthy:
            return {
                "status": "healthy",
                "response_time_ms": response_time_ms,
                "type": "postgresql" if "postgresql" in get_settings().database.url.lower() else "sqlite"
            }
        else:
            return {
                "status": "unhealthy",
                "response_time_ms": response_time_ms,
                "error": "Database connection check failed"
            }
    except Exception as e:
        logger.error(f"Database health check error: {e}")
        return {"status": "unhealthy", "error": str(e)}


async def check_services_health() -> dict:
    """Verificar salud de los servicios"""
    try:
        services_status = {}
        services_available = []
        
        # Verificar Tesseract OCR
        try:
            import pytesseract
            pytesseract.get_tesseract_version()
            services_available.append("tesseract")
            services_status["tesseract"] = "available"
        except Exception as e:
            services_status["tesseract"] = f"unavailable: {str(e)}"
        
        # Verificar servicios OCR y LLM de forma más eficiente
        # Crear instancias solo una vez y reutilizar
        ocr_service = None
        extraction_service = None
        
        # Verificar Google Vision OCR
        try:
            if ocr_service is None:
                from ..services.optimal_ocr_service import OptimalOCRService
                ocr_service = OptimalOCRService()
            if ocr_service.google_client is not None:
                services_available.append("google_vision")
                services_status["google_vision"] = "available"
            else:
                services_status["google_vision"] = "not_configured"
        except Exception as e:
            services_status["google_vision"] = f"unavailable: {str(e)}"
        
        # Verificar AWS Textract (reutilizar instancia de ocr_service)
        try:
            if ocr_service is None:
                from ..services.optimal_ocr_service import OptimalOCRService
                ocr_service = OptimalOCRService()
            if ocr_service.aws_textract is not None:
                services_available.append("aws_textract")
                services_status["aws_textract"] = "available"
            else:
                services_status["aws_textract"] = "not_configured"
        except Exception as e:
            services_status["aws_textract"] = f"unavailable: {str(e)}"
        
        # Verificar OpenAI/LLM
        try:
            if extraction_service is None:
                from ..services.intelligent_extraction_service import IntelligentExtractionService
                extraction_service = IntelligentExtractionService()
            if extraction_service.openai_client is not None:
                services_available.append("openai")
                services_status["openai"] = "available"
            else:
                services_status["openai"] = "not_configured"
        except Exception as e:
            services_status["openai"] = f"unavailable: {str(e)}"
        
        # Verificar spaCy (reutilizar instancia de extraction_service)
        try:
            if extraction_service is None:
                from ..services.intelligent_extraction_service import IntelligentExtractionService
                extraction_service = IntelligentExtractionService()
            if extraction_service.nlp is not None:
                services_available.append("spacy")
                services_status["spacy"] = "available"
            else:
                services_status["spacy"] = "not_configured"
        except Exception as e:
            services_status["spacy"] = f"unavailable: {str(e)}"
        
        # Al menos Tesseract debe estar disponible para que el sistema funcione
        overall_status = "healthy" if "tesseract" in services_available else "degraded"
        
        return {
            "status": overall_status,
            "services": services_status,
            "available_services": services_available
        }
    except Exception as e:
        logger.error(f"Services health check error: {e}")
        return {"status": "unhealthy", "error": str(e)}


async def check_cache_health() -> dict:
    """Verificar salud del cache"""
    try:
        start_time = time.time()
        is_healthy = is_redis_healthy()
        response_time_ms = int((time.time() - start_time) * 1000)
        
        redis_client = get_redis()
        
        if is_healthy and redis_client is not None:
            # Obtener información adicional de Redis
            try:
                info = redis_client.info()
                return {
                    "status": "healthy",
                    "type": "redis",
                    "response_time_ms": response_time_ms,
                    "connected_clients": info.get("connected_clients", 0),
                    "used_memory_human": info.get("used_memory_human", "N/A"),
                    "uptime_in_seconds": info.get("uptime_in_seconds", 0)
                }
            except Exception as e:
                logger.warning(f"Could not get Redis info: {e}")
                return {
                    "status": "healthy",
                    "type": "redis",
                    "response_time_ms": response_time_ms
                }
        else:
            return {
                "status": "unavailable",
                "type": "redis",
                "response_time_ms": response_time_ms,
                "error": "Redis connection not available"
            }
    except Exception as e:
        logger.error(f"Cache health check error: {e}")
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