"""
Tests para Sistema de Cache
===========================

Tests unitarios para el sistema de cache optimizado.
"""
import pytest
import asyncio
from datetime import datetime
from src.app.services.cache_optimized import CacheService, cached, cache_invalidate


class TestCacheService:
    """Tests para CacheService"""
    
    @pytest.fixture
    def cache_service(self, mock_redis):
        """Cache service con Redis mock"""
        service = CacheService()
        service.redis_client = mock_redis
        service.memory_cache = {}
        return service
    
    @pytest.mark.asyncio
    async def test_set_and_get(self, cache_service):
        """Test establecer y obtener valores"""
        key = "test_key"
        value = {"message": "Hello, Cache!", "timestamp": datetime.utcnow().isoformat()}
        
        # Test set
        success = await cache_service.set(key, value, ttl=60)
        assert success is True
        
        # Test get
        retrieved_value = await cache_service.get(key)
        assert retrieved_value is not None
        assert retrieved_value["message"] == value["message"]
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_key(self, cache_service):
        """Test obtener clave inexistente"""
        value = await cache_service.get("nonexistent_key")
        assert value is None
        
        # Test con valor por defecto
        default_value = "default"
        value = await cache_service.get("nonexistent_key", default=default_value)
        assert value == default_value
    
    @pytest.mark.asyncio
    async def test_exists(self, cache_service):
        """Test verificar existencia de claves"""
        key = "test_key"
        value = "test_value"
        
        # Clave no existe
        exists = await cache_service.exists(key)
        assert exists is False
        
        # Establecer clave
        await cache_service.set(key, value)
        
        # Clave existe
        exists = await cache_service.exists(key)
        assert exists is True
    
    @pytest.mark.asyncio
    async def test_delete(self, cache_service):
        """Test eliminar claves"""
        key = "test_key"
        value = "test_value"
        
        # Establecer clave
        await cache_service.set(key, value)
        
        # Verificar que existe
        exists = await cache_service.exists(key)
        assert exists is True
        
        # Eliminar clave
        deleted = await cache_service.delete(key)
        assert deleted is True
        
        # Verificar que no existe
        exists = await cache_service.exists(key)
        assert exists is False
    
    @pytest.mark.asyncio
    async def test_clear(self, cache_service):
        """Test limpiar cache"""
        # Establecer múltiples claves
        await cache_service.set("key1", "value1")
        await cache_service.set("key2", "value2")
        await cache_service.set("key3", "value3")
        
        # Verificar que existen
        assert await cache_service.exists("key1") is True
        assert await cache_service.exists("key2") is True
        assert await cache_service.exists("key3") is True
        
        # Limpiar todo
        cleared = await cache_service.clear()
        assert cleared is True
        
        # Verificar que no existen
        assert await cache_service.exists("key1") is False
        assert await cache_service.exists("key2") is False
        assert await cache_service.exists("key3") is False
    
    @pytest.mark.asyncio
    async def test_clear_with_pattern(self, cache_service):
        """Test limpiar cache con patrón"""
        # Establecer claves con diferentes patrones
        await cache_service.set("documents:1", "doc1")
        await cache_service.set("documents:2", "doc2")
        await cache_service.set("users:1", "user1")
        await cache_service.set("stats:overview", "stats")
        
        # Limpiar solo documentos
        cleared = await cache_service.clear("documents:*")
        assert cleared is True
        
        # Verificar que solo se eliminaron las claves de documentos
        assert await cache_service.exists("documents:1") is False
        assert await cache_service.exists("documents:2") is False
        assert await cache_service.exists("users:1") is True
        assert await cache_service.exists("stats:overview") is True
    
    @pytest.mark.asyncio
    async def test_get_stats(self, cache_service):
        """Test obtener estadísticas"""
        stats = await cache_service.get_stats()
        
        assert isinstance(stats, dict)
        assert "memory_cache" in stats
        assert "redis" in stats
        
        # Verificar estructura de estadísticas de memoria
        memory_stats = stats["memory_cache"]
        assert "size" in memory_stats
        assert "max_size" in memory_stats
        assert "ttl" in memory_stats
        
        # Verificar estructura de estadísticas de Redis
        redis_stats = stats["redis"]
        assert "available" in redis_stats
        assert "connected" in redis_stats
    
    @pytest.mark.asyncio
    async def test_serialization(self, cache_service):
        """Test serialización de diferentes tipos de datos"""
        # Test con datos simples (JSON)
        simple_data = {"key": "value", "number": 123, "boolean": True}
        await cache_service.set("simple", simple_data)
        retrieved = await cache_service.get("simple")
        assert retrieved == simple_data
        
        # Test con datos complejos (Pickle)
        complex_data = {
            "datetime": datetime.now(),
            "list": [1, 2, 3],
            "nested": {"inner": "value"}
        }
        await cache_service.set("complex", complex_data)
        retrieved = await cache_service.get("complex")
        assert retrieved["list"] == complex_data["list"]
        assert retrieved["nested"]["inner"] == complex_data["nested"]["inner"]
    
    @pytest.mark.asyncio
    async def test_ttl_expiration(self, cache_service):
        """Test expiración de TTL"""
        key = "ttl_test"
        value = "test_value"
        
        # Establecer con TTL muy corto
        await cache_service.set(key, value, ttl=1)
        
        # Verificar que existe inmediatamente
        assert await cache_service.exists(key) is True
        
        # Esperar a que expire
        await asyncio.sleep(1.1)
        
        # Verificar que ya no existe
        assert await cache_service.exists(key) is False
    
    @pytest.mark.asyncio
    async def test_memory_cache_cleanup(self, cache_service):
        """Test limpieza automática del cache en memoria"""
        # Configurar tamaño pequeño para testing
        cache_service.memory_cache_size = 3
        
        # Llenar el cache
        for i in range(5):
            await cache_service.set(f"key_{i}", f"value_{i}")
        
        # Verificar que solo quedan los últimos 3
        assert len(cache_service.memory_cache) <= 3
        
        # Verificar que las claves más antiguas fueron eliminadas
        assert "key_0" not in cache_service.memory_cache
        assert "key_1" not in cache_service.memory_cache


class TestCacheDecorators:
    """Tests para decoradores de cache"""
    
    @pytest.mark.asyncio
    async def test_cached_decorator(self, mock_cache_service):
        """Test decorador @cached"""
        call_count = 0
        
        @cached(ttl=300, key_prefix="test_function")
        async def expensive_function(param1, param2=None):
            nonlocal call_count
            call_count += 1
            return {"result": param1 + (param2 or 0), "call_count": call_count}
        
        # Primera llamada - debe ejecutar la función
        result1 = await expensive_function(10, param2=5)
        assert result1["result"] == 15
        assert result1["call_count"] == 1
        assert call_count == 1
        
        # Segunda llamada con mismos parámetros - debe usar cache
        result2 = await expensive_function(10, param2=5)
        assert result2["result"] == 15
        assert result2["call_count"] == 1  # Debe ser el mismo resultado
        assert call_count == 1  # La función no se ejecutó de nuevo
        
        # Tercera llamada con diferentes parámetros - debe ejecutar la función
        result3 = await expensive_function(20, param2=10)
        assert result3["result"] == 30
        assert result3["call_count"] == 2
        assert call_count == 2
    
    @pytest.mark.asyncio
    async def test_cache_invalidate_decorator(self, mock_cache_service):
        """Test decorador @cache_invalidate"""
        call_count = 0
        
        @cache_invalidate("test_pattern")
        async def update_function(data):
            nonlocal call_count
            call_count += 1
            return {"updated": data, "call_count": call_count}
        
        # Establecer algunos valores en cache
        await mock_cache_service.set("test_pattern:key1", "value1")
        await mock_cache_service.set("test_pattern:key2", "value2")
        await mock_cache_service.set("other_pattern:key3", "value3")
        
        # Verificar que existen
        assert await mock_cache_service.exists("test_pattern:key1") is True
        assert await mock_cache_service.exists("test_pattern:key2") is True
        assert await mock_cache_service.exists("other_pattern:key3") is True
        
        # Ejecutar función que invalida cache
        result = await update_function("new_data")
        assert result["updated"] == "new_data"
        assert call_count == 1
        
        # Verificar que las claves del patrón fueron eliminadas
        assert await mock_cache_service.exists("test_pattern:key1") is False
        assert await mock_cache_service.exists("test_pattern:key2") is False
        assert await mock_cache_service.exists("other_pattern:key3") is True  # No debe ser afectada


class TestCacheIntegration:
    """Tests de integración del sistema de cache"""
    
    @pytest.mark.asyncio
    async def test_cache_with_repository(self, document_repository, mock_cache_service):
        """Test integración de cache con repository"""
        # Mock del cache service en el repository
        with patch('src.app.repositories.document_repository.cache_service', mock_cache_service):
            # Crear documento
            document = document_repository.create(
                filename="cache_test.pdf",
                original_filename="cache_test.pdf",
                file_path="/uploads/cache_test.pdf",
                file_size=1024,
                mime_type="application/pdf",
                document_type="factura",
                status="uploaded"
            )
            
            # Primera consulta - debe ejecutar query y cachear
            documents1 = document_repository.get_by_type("factura")
            assert len(documents1) >= 1
            
            # Segunda consulta - debe usar cache
            documents2 = document_repository.get_by_type("factura")
            assert len(documents2) >= 1
            assert documents1 == documents2
            
            # Verificar que se usó el cache
            cache_key = "documents_by_type:factura:0:20"
            cached_value = await mock_cache_service.get(cache_key)
            assert cached_value is not None
            
            # Limpiar
            document_repository.delete(document.id)


