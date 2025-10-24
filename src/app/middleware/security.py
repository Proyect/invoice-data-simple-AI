"""
Security Middleware
==================

Middleware para seguridad y protección de la aplicación.
"""
import logging
from typing import Callable
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware para seguridad"""
    
    def __init__(self, app, max_request_size: int = 10 * 1024 * 1024):  # 10MB
        super().__init__(app)
        self.max_request_size = max_request_size
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Interceptar request y aplicar medidas de seguridad"""
        
        # Verificar tamaño del request
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_request_size:
            raise HTTPException(
                status_code=413,
                detail=f"Request too large. Maximum size: {self.max_request_size} bytes"
            )
        
        # Verificar headers de seguridad
        await self._check_security_headers(request)
        
        # Procesar request
        response = await call_next(request)
        
        # Agregar headers de seguridad
        self._add_security_headers(response)
        
        return response
    
    async def _check_security_headers(self, request: Request) -> None:
        """Verificar headers de seguridad en el request"""
        
        # Verificar User-Agent (básico)
        user_agent = request.headers.get("user-agent", "")
        if not user_agent or len(user_agent) > 500:
            logger.warning(f"Suspicious User-Agent: {user_agent}")
        
        # Verificar Content-Type para uploads
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")
            if "multipart/form-data" in content_type:
                # Verificar que sea un upload válido
                if not any(key in content_type for key in ["boundary", "form-data"]):
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid multipart content type"
                    )
    
    def _add_security_headers(self, response: Response) -> None:
        """Agregar headers de seguridad a la respuesta"""
        
        # Headers de seguridad estándar
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        }
        
        # Agregar headers
        for header, value in security_headers.items():
            response.headers[header] = value
        
        # Content Security Policy (básico)
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp
