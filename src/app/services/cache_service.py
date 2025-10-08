import json
import pickle
from typing import Any, Optional
from app.core.database import redis_client
import logging

logger = logging.getLogger(__name__)

class CacheService:
    """Servicio de cache usando Redis"""
    
    def __init__(self):
        self.redis = redis_client
        self.default_ttl = 3600  # 1 hora
    
    async def get(self, key: str) -> Optional[Any]:
        """Obtener valor del cache"""
        if not self.redis:
            return None
        
        try:
            value = self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error obteniendo cache {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Guardar valor en cache"""
        if not self.redis:
            return False
        
        try:
            ttl = ttl or self.default_ttl
            serialized_value = json.dumps(value, default=str)
            return self.redis.setex(key, ttl, serialized_value)
        except Exception as e:
            logger.error(f"Error guardando cache {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Eliminar valor del cache"""
        if not self.redis:
            return False
        
        try:
            return bool(self.redis.delete(key))
        except Exception as e:
            logger.error(f"Error eliminando cache {key}: {e}")
            return False
    
    async def get_or_set(self, key: str, func, ttl: int = None, *args, **kwargs) -> Any:
        """Obtener del cache o ejecutar función y guardar resultado"""
        # Intentar obtener del cache
        cached_value = await self.get(key)
        if cached_value is not None:
            return cached_value
        
        # Ejecutar función
        import asyncio
        if asyncio.iscoroutinefunction(func):
            value = await func(*args, **kwargs)
        else:
            value = func(*args, **kwargs)
        
        # Guardar en cache
        await self.set(key, value, ttl)
        return value
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidar cache por patrón"""
        if not self.redis:
            return 0
        
        try:
            keys = self.redis.keys(pattern)
            if keys:
                return self.redis.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Error invalidando cache patrón {pattern}: {e}")
            return 0

# Instancia global
cache_service = CacheService()
