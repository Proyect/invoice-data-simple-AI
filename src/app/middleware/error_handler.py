"""
Error Handler Middleware
========================

Middleware para manejo centralizado de errores con códigos de error personalizados.
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

# Códigos de error personalizados
class ErrorCodes:
    """Códigos de error del sistema"""
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    INVALID_FILE = "INVALID_FILE"
    PROCESSING_ERROR = "PROCESSING_ERROR"


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
        # Mapear códigos de estado HTTP a códigos de error personalizados
        error_code_map = {
            400: ErrorCodes.VALIDATION_ERROR,
            401: ErrorCodes.UNAUTHORIZED,
            403: ErrorCodes.FORBIDDEN,
            404: ErrorCodes.NOT_FOUND,
            429: ErrorCodes.RATE_LIMIT_EXCEEDED,
            500: ErrorCodes.INTERNAL_ERROR,
            503: ErrorCodes.SERVICE_UNAVAILABLE,
        }
        
        error_code = error_code_map.get(exc.status_code, f"HTTP_{exc.status_code}")
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "type": "HTTPException",
                    "code": exc.status_code,
                    "error_code": error_code,
                    "message": exc.detail if isinstance(exc.detail, str) else "Error en la solicitud",
                    "details": exc.detail if not isinstance(exc.detail, str) else None,
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
                    "error_code": ErrorCodes.VALIDATION_ERROR,
                    "message": "Error de validación en los datos de entrada. Por favor, revisa los campos enviados.",
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
        # Identificar tipo de error común
        error_type = type(exc).__name__
        error_message = str(exc)
        
        # Mensajes más específicos según el tipo de error
        if "database" in error_message.lower() or "sql" in error_message.lower():
            user_message = "Error de conexión con la base de datos. Por favor, intenta nuevamente."
        elif "redis" in error_message.lower() or "cache" in error_message.lower():
            user_message = "Error de conexión con el sistema de cache. El sistema continuará funcionando sin cache."
        elif "ocr" in error_message.lower() or "tesseract" in error_message.lower():
            user_message = "Error al procesar el documento. Por favor, verifica que el archivo sea válido."
        elif "file" in error_message.lower() or "upload" in error_message.lower():
            user_message = "Error al procesar el archivo. Por favor, verifica el formato y tamaño del archivo."
        else:
            user_message = "Error interno del servidor. Por favor, contacta al administrador si el problema persiste."
        
        if self.settings.debug:
            # En desarrollo, mostrar detalles del error
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "type": "InternalServerError",
                        "code": 500,
                        "error_code": ErrorCodes.INTERNAL_ERROR,
                        "message": user_message,
                        "details": {
                            "exception_type": error_type,
                            "exception_message": error_message,
                        },
                    }
                }
            )
        else:
            # En producción, ocultar detalles pero dar mensaje útil
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "type": "InternalServerError",
                        "code": 500,
                        "error_code": ErrorCodes.INTERNAL_ERROR,
                        "message": user_message,
                        "details": None,
                    }
                }
            )
