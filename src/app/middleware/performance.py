"""
Performance Middleware
======================

Middleware para monitoreo de rendimiento y optimización.
"""
import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware para monitoreo de rendimiento"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Interceptar request y medir rendimiento"""
        
        # Marcar inicio del request
        start_time = time.time()
        
        # Procesar request
        response = await call_next(request)
        
        # Calcular tiempo de procesamiento
        process_time = time.time() - start_time
        
        # Log de rendimiento
        logger.info(
            f"Request processed: {request.method} {request.url.path} "
            f"Status: {response.status_code} "
            f"Time: {process_time:.4f}s"
        )
        
        # Agregar headers de rendimiento
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = getattr(request.state, "request_id", "unknown")
        
        # Alertas de rendimiento lento
        if process_time > 5.0:  # Más de 5 segundos
            logger.warning(f"Slow request detected: {request.url.path} took {process_time:.4f}s")
        elif process_time > 1.0:  # Más de 1 segundo
            logger.info(f"Moderate request time: {request.url.path} took {process_time:.4f}s")
        
        return response
