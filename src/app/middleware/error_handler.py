"""
Error Handler Middleware
========================

Middleware para manejo centralizado de errores.
"""
import logging
from typing import Union
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import ValidationError

from ..core.environment import get_settings

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware:
    """Middleware para manejo centralizado de errores"""
    
    def __init__(self, app):
        self.app = app
        self.settings = get_settings()
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        
        try:
            await self.app(scope, receive, send)
        except Exception as exc:
            response = await self.handle_exception(request, exc)
            await response(scope, receive, send)
    
    async def handle_exception(self, request: Request, exc: Exception) -> JSONResponse:
        """Manejar excepción y generar respuesta apropiada"""
        
        # Log del error
        logger.error(f"Error en {request.method} {request.url}: {exc}", exc_info=True)
        
        # Determinar tipo de error y respuesta
        if isinstance(exc, HTTPException):
            return self._handle_http_exception(exc)
        elif isinstance(exc, RequestValidationError):
            return self._handle_validation_error(exc)
        elif isinstance(exc, StarletteHTTPException):
            return self._handle_starlette_http_exception(exc)
        elif isinstance(exc, ValidationError):
            return self._handle_pydantic_validation_error(exc)
        else:
            return self._handle_generic_error(exc)
    
    def _handle_http_exception(self, exc: HTTPException) -> JSONResponse:
        """Manejar HTTPException de FastAPI"""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "type": "HTTPException",
                    "code": exc.status_code,
                    "message": exc.detail,
                    "details": None,
                }
            }
        )
    
    def _handle_validation_error(self, exc: RequestValidationError) -> JSONResponse:
        """Manejar errores de validación de request"""
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "type": "ValidationError",
                    "code": 422,
                    "message": "Error de validación en los datos de entrada",
                    "details": exc.errors(),
                }
            }
        )
    
    def _handle_starlette_http_exception(self, exc: StarletteHTTPException) -> JSONResponse:
        """Manejar HTTPException de Starlette"""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "type": "HTTPException",
                    "code": exc.status_code,
                    "message": exc.detail,
                    "details": None,
                }
            }
        )
    
    def _handle_pydantic_validation_error(self, exc: ValidationError) -> JSONResponse:
        """Manejar errores de validación de Pydantic"""
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "type": "ValidationError",
                    "code": 422,
                    "message": "Error de validación en los datos",
                    "details": exc.errors(),
                }
            }
        )
    
    def _handle_generic_error(self, exc: Exception) -> JSONResponse:
        """Manejar errores genéricos"""
        if self.settings.debug:
            # En desarrollo, mostrar detalles del error
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "type": "InternalServerError",
                        "code": 500,
                        "message": "Error interno del servidor",
                        "details": {
                            "exception_type": type(exc).__name__,
                            "exception_message": str(exc),
                        } if self.settings.debug else None,
                    }
                }
            )
        else:
            # En producción, ocultar detalles
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "type": "InternalServerError",
                        "code": 500,
                        "message": "Error interno del servidor",
                        "details": None,
                    }
                }
            )
