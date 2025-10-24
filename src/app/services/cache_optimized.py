"""
Sistema de Cache Optimizado
===========================

Sistema de cache multi-nivel con Redis y memoria local.
"""
import json
import logging
import pickle
from typing import Any, Optional, Union, Dict, List
from datetime import datetime, timedelta
from functools import wraps
import hashlib

import redis
from redis.exceptions import RedisError

from ..core.database import get_redis
from ..core.environment import get_settings

logger = logging.getLogger(__name__)


class CacheService:
    """Servicio de cache optimizado con múltiples niveles"""
    
    def __init__(self):
        self.settings = get_settings()
        self.redis_client: Optional[redis.Redis] = None
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self.memory_cache_size = 1000  # Máximo 1000 items en memoria
        self.memory_cache_ttl = 300  # 5 minutos TTL para memoria
        
        # Inicializar Redis
        self._init_redis()
    
    def _init_redis(self) -> None:
        """Inicializar cliente Redis"""
        try:
            self.redis_client = get_redis()
            if self.redis_client:
                # Test de conexión
                self.redis_client.ping()
                logger.info("✅ Cache Redis inicializado")
            else:
                logger.warning("⚠️ Redis no disponible, usando solo cache en memoria")
        except Exception as e:
            logger.error(f"❌ Error inicializando Redis: {e}")
            self.redis_client = None
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generar clave de cache única"""
        # Combinar argumentos
        key_parts = [prefix] + [str(arg) for arg in args]
        
        # Agregar kwargs ordenados
        if kwargs:
            sorted_kwargs = sorted(kwargs.items())
            key_parts.extend([f"{k}={v}" for k, v in sorted_kwargs])
        
        # Crear hash de la clave
        key_string = ":".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _serialize_value(self, value: Any) -> str:
        """Serializar valor para almacenamiento"""
        try:
            # Intentar JSON primero (más eficiente para datos simples)
            return json.dumps(value, default=str)
        except (TypeError, ValueError):
            # Fallback a pickle para objetos complejos
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
    
    def _clean_memory_cache(self) -> None:
        """Limpiar cache en memoria de items expirados"""
        current_time = datetime.utcnow()
        expired_keys = []
        
        for key, item in self.memory_cache.items():
            if 'expires_at' in item and current_time >= item['expires_at']:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.memory_cache[key]
        
        # Si aún hay demasiados items, eliminar los más antiguos
        if len(self.memory_cache) > self.memory_cache_size:
            sorted_items = sorted(
                self.memory_cache.items(),
                key=lambda x: x[1].get('created_at', datetime.min)
            )
            
            items_to_remove = len(self.memory_cache) - self.memory_cache_size
            for key, _ in sorted_items[:items_to_remove]:
                del self.memory_cache[key]
    
    async def get(self, key: str, default: Any = None) -> Any:
        """Obtener valor del cache"""
        # 1. Intentar cache en memoria primero
        if key in self.memory_cache:
            item = self.memory_cache[key]
            if self._is_memory_cache_valid(item):
                logger.debug(f"Cache hit (memory): {key}")
                return item['value']
            else:
                # Item expirado, eliminarlo
                del self.memory_cache[key]
        
        # 2. Intentar Redis
        if self.redis_client:
            try:
                redis_value = self.redis_client.get(key)
                if redis_value:
                    # Determinar si es JSON o pickle
                    is_pickle = not redis_value.startswith(b'{') and not redis_value.startswith(b'[')
                    value = self._deserialize_value(redis_value.decode(), is_pickle)
                    
                    if value is not None:
                        # Almacenar en cache en memoria para acceso rápido
                        self.memory_cache[key] = {
                            'value': value,
                            'created_at': datetime.utcnow(),
                            'expires_at': datetime.utcnow() + timedelta(seconds=self.memory_cache_ttl)
                        }
                        
                        logger.debug(f"Cache hit (Redis): {key}")
                        return value
            except RedisError as e:
                logger.warning(f"Error accediendo a Redis: {e}")
        
        logger.debug(f"Cache miss: {key}")
        return default
    
    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Establecer valor en cache"""
        try:
            # 1. Almacenar en memoria
            self.memory_cache[key] = {
                'value': value,
                'created_at': datetime.utcnow(),
                'expires_at': datetime.utcnow() + timedelta(seconds=min(ttl, self.memory_cache_ttl))
            }
            
            # 2. Almacenar en Redis
            if self.redis_client:
                serialized_value = self._serialize_value(value)
                self.redis_client.setex(key, ttl, serialized_value)
            
            # 3. Limpiar cache en memoria si es necesario
            self._clean_memory_cache()
            
            logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
            return True
            
        except Exception as e:
            logger.error(f"Error estableciendo cache: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Eliminar valor del cache"""
        try:
            # 1. Eliminar de memoria
            if key in self.memory_cache:
                del self.memory_cache[key]
            
            # 2. Eliminar de Redis
            if self.redis_client:
                self.redis_client.delete(key)
            
            logger.debug(f"Cache delete: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Error eliminando cache: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Verificar si una clave existe en cache"""
        # Verificar memoria primero
        if key in self.memory_cache and self._is_memory_cache_valid(self.memory_cache[key]):
            return True
        
        # Verificar Redis
        if self.redis_client:
            try:
                return bool(self.redis_client.exists(key))
            except RedisError:
                pass
        
        return False
    
    async def clear(self, pattern: str = None) -> bool:
        """Limpiar cache"""
        try:
            # Limpiar memoria
            if pattern:
                keys_to_delete = [k for k in self.memory_cache.keys() if pattern in k]
                for key in keys_to_delete:
                    del self.memory_cache[key]
            else:
                self.memory_cache.clear()
            
            # Limpiar Redis
            if self.redis_client:
                if pattern:
                    keys = self.redis_client.keys(pattern)
                    if keys:
                        self.redis_client.delete(*keys)
                else:
                    self.redis_client.flushdb()
            
            logger.info(f"Cache cleared: {pattern or 'all'}")
            return True
            
        except Exception as e:
            logger.error(f"Error limpiando cache: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del cache"""
        stats = {
            'memory_cache': {
                'size': len(self.memory_cache),
                'max_size': self.memory_cache_size,
                'ttl': self.memory_cache_ttl
            },
            'redis': {
                'available': self.redis_client is not None,
                'connected': False
            }
        }
        
        if self.redis_client:
            try:
                info = self.redis_client.info()
                stats['redis'].update({
                    'connected': True,
                    'used_memory': info.get('used_memory_human', 'N/A'),
                    'connected_clients': info.get('connected_clients', 0),
                    'keyspace_hits': info.get('keyspace_hits', 0),
                    'keyspace_misses': info.get('keyspace_misses', 0)
                })
            except RedisError:
                pass
        
        return stats


# Instancia global del servicio de cache
cache_service = CacheService()


def cached(ttl: int = 300, key_prefix: str = ""):
    """Decorator para cachear resultados de funciones"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generar clave de cache
            cache_key = cache_service._generate_key(
                key_prefix or func.__name__,
                *args,
                **kwargs
            )
            
            # Intentar obtener del cache
            result = await cache_service.get(cache_key)
            if result is not None:
                return result
            
            # Ejecutar función y cachear resultado
            result = await func(*args, **kwargs)
            await cache_service.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


def cache_invalidate(pattern: str = None):
    """Decorator para invalidar cache después de operaciones"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            
            # Invalidar cache
            if pattern:
                await cache_service.clear(pattern)
            else:
                # Invalidar por nombre de función
                await cache_service.clear(f"*{func.__name__}*")
            
            return result
        
        return wrapper
    return decorator
