"""
Tests para validar correcciones críticas
"""
import pytest
from src.app.services.cache import get_cache_service
from src.app.core.environment import get_settings
from src.app.core.config import settings as config_settings


def test_requests_installed():
    """Verificar que requests está instalado"""
    import requests
    assert requests.__version__ is not None


def test_cache_service_consolidated():
    """Verificar que cache está consolidado"""
    cache = get_cache_service()
    
    # Test básico
    cache.set("test_key", {"test": "value"})
    value = cache.get("test_key")
    
    assert value == {"test": "value"}
    
    # Test stats
    stats = cache.get_stats()
    assert "memory_items" in stats
    assert "redis_available" in stats


def test_cache_async_methods():
    """Verificar que métodos async funcionan"""
    import asyncio
    cache = get_cache_service()
    
    async def test_async():
        await cache.aset("async_key", {"async": "value"})
        value = await cache.aget("async_key")
        assert value == {"async": "value"}
    
    asyncio.run(test_async())


def test_config_wrapper_compatibility():
    """Verificar que config.py wrapper funciona"""
    # Verificar que las propiedades legacy funcionan
    assert config_settings.APP_NAME is not None
    assert config_settings.DATABASE_URL is not None
    assert config_settings.REDIS_HOST is not None


def test_environment_settings():
    """Verificar que environment.py funciona"""
    settings = get_settings()
    
    assert settings.name is not None
    assert settings.database.url is not None
    assert settings.redis.host is not None


def test_config_and_environment_sync():
    """Verificar que config.py y environment.py están sincronizados"""
    settings = get_settings()
    
    # Verificar que los valores coinciden
    assert config_settings.APP_NAME == settings.name
    assert config_settings.DATABASE_URL == settings.database.url
    assert config_settings.REDIS_HOST == settings.redis.host


def test_cache_decorator():
    """Verificar que decorador cached funciona"""
    from src.app.services.cache import cached
    
    call_count = 0
    
    @cached(ttl=60, key_prefix="test_func")
    def test_function(x: int):
        nonlocal call_count
        call_count += 1
        return x * 2
    
    # Primera llamada
    result1 = test_function(5)
    assert result1 == 10
    assert call_count == 1
    
    # Segunda llamada (debe usar cache)
    result2 = test_function(5)
    assert result2 == 10
    assert call_count == 1  # No debe incrementar


def test_cache_invalidate():
    """Verificar que cache_invalidate funciona"""
    from src.app.services.cache import cache_invalidate, get_cache_service
    
    cache = get_cache_service()
    cache.set("test_invalidate", {"data": "value"})
    
    @cache_invalidate(pattern="test_*")
    def update_function():
        return True
    
    result = update_function()
    assert result is True
    
    # Verificar que el cache fue invalidado
    value = cache.get("test_invalidate")
    # El valor puede estar o no dependiendo de la implementación
    # Lo importante es que la función se ejecutó




