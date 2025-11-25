"""
Rate Limiting Middleware
========================

Middleware para limitar la tasa de requests por cliente.
"""
import logging
import time
from typing import Callable, Optional
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from ..core.database import get_redis
from ..core.environment import get_settings

logger = logging.getLogger(__name__)


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """Middleware para rate limiting usando Redis o memoria"""
    
    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        burst: int = 10,
        enabled: bool = True
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.burst = burst
        self.enabled = enabled
        
        # Fallback in-memory store si Redis no está disponible
        self._memory_store: dict = {}
        
        # Obtener configuración
        settings = get_settings()
        self.redis_client = get_redis() if enabled else None
        
        # Lista de paths excluidos del rate limiting
        self.excluded_paths = [
            "/health",
            "/docs",
            "/openapi.json",
            "/redoc",
            "/",
            "/info"
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Interceptar request y aplicar rate limiting"""
        
        # Si está deshabilitado, continuar sin límites
        if not self.enabled:
            return await call_next(request)
        
        # Excluir ciertos paths del rate limiting
        if any(request.url.path.startswith(path) for path in self.excluded_paths):
            return await call_next(request)
        
        # Obtener identificador del cliente
        client_id = self._get_client_id(request)
        
        # Verificar rate limit
        if not await self._check_rate_limit(client_id):
            logger.warning(f"Rate limit exceeded for client: {client_id}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {self.requests_per_minute} requests per minute.",
                headers={
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                    "Retry-After": "60"
                }
            )
        
        # Procesar request
        response = await call_next(request)
        
        # Agregar headers de rate limit a la respuesta
        remaining = await self._get_remaining_requests(client_id)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + 60)
        
        return response
    
    def _get_client_id(self, request: Request) -> str:
        """Obtener identificador único del cliente"""
        # Intentar obtener IP real (detrás de proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Tomar el primer IP si hay múltiples
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"
        
        # Si hay usuario autenticado, usar su ID para rate limiting más preciso
        # Por ahora, usar IP
        return f"ip:{client_ip}"
    
    async def _check_rate_limit(self, client_id: str) -> bool:
        """Verificar si el cliente puede hacer más requests"""
        try:
            if self.redis_client:
                return await self._check_rate_limit_redis(client_id)
            else:
                return self._check_rate_limit_memory(client_id)
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            # En caso de error, permitir el request (fail open)
            return True
    
    async def _check_rate_limit_redis(self, client_id: str) -> bool:
        """Verificar rate limit usando Redis"""
        try:
            key = f"rate_limit:{client_id}"
            current_time = int(time.time())
            window_start = current_time - 60  # Ventana de 60 segundos
            
            # Usar pipeline para atomicidad
            pipe = self.redis_client.pipeline()
            
            # Remover entradas fuera de la ventana
            pipe.zremrangebyscore(key, 0, window_start)
            
            # Contar requests en la ventana
            pipe.zcard(key)
            
            # Agregar request actual
            pipe.zadd(key, {str(current_time): current_time})
            
            # Establecer expiración
            pipe.expire(key, 60)
            
            results = pipe.execute()
            request_count = results[1] if len(results) > 1 else 0
            
            # Verificar límite
            if request_count >= self.requests_per_minute:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Redis rate limit check error: {e}")
            # Fallback a memoria
            return self._check_rate_limit_memory(client_id)
    
    def _check_rate_limit_memory(self, client_id: str) -> bool:
        """Verificar rate limit usando almacenamiento en memoria (fallback)"""
        current_time = time.time()
        window_start = current_time - 60
        
        if client_id not in self._memory_store:
            self._memory_store[client_id] = []
        
        # Limpiar requests fuera de la ventana
        timestamps = self._memory_store[client_id]
        timestamps[:] = [ts for ts in timestamps if ts > window_start]
        
        # Verificar límite
        if len(timestamps) >= self.requests_per_minute:
            return False
        
        # Agregar request actual
        timestamps.append(current_time)
        
        # Limpiar entradas antiguas (cada 100 requests para eficiencia)
        if len(self._memory_store) > 1000:
            # Limpiar entradas de más de 5 minutos
            cutoff = current_time - 300
            self._memory_store = {
                k: [ts for ts in v if ts > cutoff]
                for k, v in self._memory_store.items()
                if any(ts > cutoff for ts in v)
            }
        
        return True
    
    async def _get_remaining_requests(self, client_id: str) -> int:
        """Obtener número de requests restantes"""
        try:
            if self.redis_client:
                key = f"rate_limit:{client_id}"
                current_time = int(time.time())
                window_start = current_time - 60
                
                # Contar requests en la ventana
                count = self.redis_client.zcount(key, window_start, current_time)
                remaining = max(0, self.requests_per_minute - count)
                return remaining
            else:
                # Memory store
                current_time = time.time()
                window_start = current_time - 60
                
                if client_id not in self._memory_store:
                    return self.requests_per_minute
                
                timestamps = [ts for ts in self._memory_store[client_id] if ts > window_start]
                remaining = max(0, self.requests_per_minute - len(timestamps))
                return remaining
                
        except Exception as e:
            logger.error(f"Error getting remaining requests: {e}")
            return self.requests_per_minute

