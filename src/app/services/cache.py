"""
Servicio de Cache Consolidado
=============================
Combina cache_service.py y cache_optimized.py en un único servicio
"""
import json
import logging
import pickle
from typing import Any, Optional, Dict, Callable
from datetime import datetime, timedelta
from functools import wraps
import hashlib

import redis
from redis.exceptions import RedisError

from ..core.database import get_redis
from ..core.environment import get_settings

logger = logging.getLogger(__name__)


class CacheService:
    """
    Servicio de cache consolidado con múltiples niveles:
    - Nivel 1: Memoria local (LRU cache)
    - Nivel 2: Redis (distribuido)
    - Fallback: Sin cache si Redis no está disponible
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.redis_client: Optional[redis.Redis] = None
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self.memory_cache_size = 1000
        self.memory_cache_ttl = 300  # 5 minutos
        self.default_ttl = 3600  # 1 hora por defecto
        
        self._init_redis()
    
    def _init_redis(self) -> None:
        """Inicializar cliente Redis"""
        try:
            self.redis_client = get_redis()
            if self.redis_client:
                self.redis_client.ping()
                logger.info("✅ Cache Redis inicializado")
            else:
                logger.warning("⚠️ Redis no disponible, usando solo cache en memoria")
        except Exception as e:
            logger.error(f"❌ Error inicializando Redis: {e}")
            self.redis_client = None
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generar clave de cache única"""
        key_parts = [prefix] + [str(arg) for arg in args]
        if kwargs:
            sorted_kwargs = sorted(kwargs.items())
            key_parts.extend([f"{k}={v}" for k, v in sorted_kwargs])
        key_string = ":".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _serialize_value(self, value: Any) -> str:
        """Serializar valor para almacenamiento"""
        try:
            return json.dumps(value, default=str)
        except (TypeError, ValueError):
            return pickle.dumps(value).hex()
    
    def _deserialize_value(self, value: str, is_pickle: bool = False) -> Any:
        """Deserializar valor desde almacenamiento"""
        try:
            if is_pickle:
                return pickle.loads(bytes.fromhex(value))
            else:
                return json.loads(value)
        except (json.JSONDecodeError, pickle.PickleError, ValueError) as e:
            logger.error(f"Error deserializando valor: {e}")
            return None
    
    def _is_memory_cache_valid(self, item: Dict[str, Any]) -> bool:
        """Verificar si un item del cache en memoria es válido"""
        if 'expires_at' not in item:
            return False
        return datetime.utcnow() < item['expires_at']
    
    def _set_memory(self, key: str, value: Any, ttl: int = None):
        """Establecer en cache de memoria"""
        if ttl is None:
            ttl = self.memory_cache_ttl
        
        # Limpiar si está lleno
        if len(self.memory_cache) >= self.memory_cache_size:
            oldest_key = min(
                self.memory_cache.keys(),
                key=lambda k: self.memory_cache[k].get('expires_at', datetime.min)
            )
            del self.memory_cache[oldest_key]
        
        self.memory_cache[key] = {
            'value': value,
            'created_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(seconds=ttl)
        }
    
    # Métodos síncronos (para compatibilidad)
    def get(self, key: str, default: Any = None) -> Optional[Any]:
        """Obtener valor del cache (síncrono)"""
        # Nivel 1: Memoria
        if key in self.memory_cache:
            item = self.memory_cache[key]
            if self._is_memory_cache_valid(item):
                logger.debug(f"Cache hit (memory): {key}")
                return item['value']
            else:
                del self.memory_cache[key]
        
        # Nivel 2: Redis
        if self.redis_client:
            try:
                redis_value = self.redis_client.get(key)
                if redis_value:
                    # Determinar si es JSON o pickle
                    if isinstance(redis_value, bytes):
                        is_pickle = not redis_value.startswith(b'{') and not redis_value.startswith(b'[')
                        value = self._deserialize_value(redis_value.decode(), is_pickle)
                    else:
                        value = json.loads(redis_value)
                    
                    if value is not None:
                        self._set_memory(key, value)
                        logger.debug(f"Cache hit (Redis): {key}")
                        return value
            except Exception as e:
                logger.error(f"Error obteniendo de Redis {key}: {e}")
        
        logger.debug(f"Cache miss: {key}")
        return default
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Establecer valor en cache (síncrono)"""
        if ttl is None:
            ttl = self.default_ttl
        
        try:
            # Set en memoria
            self._set_memory(key, value, min(ttl, self.memory_cache_ttl))
            
            # Set en Redis
            if self.redis_client:
                serialized = self._serialize_value(value)
                self.redis_client.setex(key, ttl, serialized)
            
            logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Error estableciendo cache {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Eliminar del cache"""
        try:
            # Eliminar de memoria
            if key in self.memory_cache:
                del self.memory_cache[key]
            
            # Eliminar de Redis
            if self.redis_client:
                self.redis_client.delete(key)
            
            logger.debug(f"Cache delete: {key}")
            return True
        except Exception as e:
            logger.error(f"Error eliminando cache {key}: {e}")
            return False
    
    # Métodos asíncronos (para compatibilidad con código async)
    async def aget(self, key: str, default: Any = None) -> Optional[Any]:
        """Obtener valor del cache (asíncrono)"""
        return self.get(key, default)
    
    async def aset(self, key: str, value: Any, ttl: int = None) -> bool:
        """Establecer valor en cache (asíncrono)"""
        return self.set(key, value, ttl)
    
    async def adelete(self, key: str) -> bool:
        """Eliminar del cache (asíncrono)"""
        return self.delete(key)
    
    async def get_or_set(self, key: str, func: Callable, ttl: int = None, *args, **kwargs) -> Any:
        """Obtener del cache o ejecutar función y guardar resultado"""
        # Intentar obtener del cache
        cached_value = await self.aget(key)
        if cached_value is not None:
            return cached_value
        
        # Ejecutar función
        import asyncio
        if asyncio.iscoroutinefunction(func):
            value = await func(*args, **kwargs)
        else:
            value = func(*args, **kwargs)
        
        # Guardar en cache
        await self.aset(key, value, ttl)
        return value
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidar cache por patrón"""
        if not self.redis_client:
            # Limpiar de memoria
            keys_to_delete = [k for k in self.memory_cache.keys() if pattern.replace('*', '') in k]
            for key in keys_to_delete:
                del self.memory_cache[key]
            return len(keys_to_delete)
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                deleted = self.redis_client.delete(*keys)
                # También eliminar de memoria
                for key in keys:
                    if isinstance(key, bytes):
                        key = key.decode()
                    if key in self.memory_cache:
                        del self.memory_cache[key]
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Error invalidando cache patrón {pattern}: {e}")
            return 0
    
    def clear(self, pattern: str = None):
        """Limpiar todo el cache"""
        if pattern:
            if self.redis_client:
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
            keys_to_delete = [k for k in self.memory_cache.keys() if pattern.replace('*', '') in k]
            for key in keys_to_delete:
                del self.memory_cache[key]
        else:
            self.memory_cache.clear()
            if self.redis_client:
                try:
                    self.redis_client.flushdb()
                except Exception as e:
                    logger.error(f"Error limpiando Redis: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del cache"""
        stats = {
            'memory_items': len(self.memory_cache),
            'memory_max_size': self.memory_cache_size,
            'redis_available': self.redis_client is not None
        }
        
        if self.redis_client:
            try:
                info = self.redis_client.info()
                stats['redis_used_memory'] = info.get('used_memory_human', 'N/A')
                stats['redis_connected_clients'] = info.get('connected_clients', 0)
            except Exception:
                pass
        
        return stats


# Singleton instance
_cache_service: Optional[CacheService] = None

def get_cache_service() -> CacheService:
    """Obtener instancia singleton del servicio de cache"""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service


# Alias para compatibilidad
cache_service = get_cache_service()


# Decorador para cachear resultados de funciones
def cached(ttl: int = 3600, key_prefix: str = ""):
    """
    Decorador para cachear resultados de funciones
    
    Uso:
        @cached(ttl=3600, key_prefix="user")
        async def get_user(user_id: int):
            # ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            cache = get_cache_service()
            
            # Generar clave de cache
            cache_key = cache._generate_key(
                key_prefix or func.__name__,
                *args,
                **kwargs
            )
            
            # Intentar obtener del cache
            cached_value = await cache.aget(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Ejecutar función
            result = await func(*args, **kwargs)
            
            # Guardar en cache
            await cache.aset(cache_key, result, ttl)
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            cache = get_cache_service()
            
            # Generar clave de cache
            cache_key = cache._generate_key(
                key_prefix or func.__name__,
                *args,
                **kwargs
            )
            
            # Intentar obtener del cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Ejecutar función
            result = func(*args, **kwargs)
            
            # Guardar en cache
            cache.set(cache_key, result, ttl)
            
            return result
        
        # Retornar wrapper apropiado según si la función es async
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def cache_invalidate(pattern: str = None):
    """
    Decorador para invalidar cache después de operaciones
    
    Uso:
        @cache_invalidate(pattern="documents_*")
        async def update_document(...):
            # ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            
            # Invalidar cache
            cache = get_cache_service()
            if pattern:
                await cache.invalidate_pattern(pattern)
            else:
                # Invalidar por nombre de función
                await cache.invalidate_pattern(f"*{func.__name__}*")
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            # Invalidar cache
            cache = get_cache_service()
            if pattern:
                # Para sync, usar clear con pattern
                cache.clear(pattern)
            else:
                cache.clear(f"*{func.__name__}*")
            
            return result
        
        # Retornar wrapper apropiado
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

