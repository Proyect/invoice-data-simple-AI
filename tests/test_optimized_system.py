#!/usr/bin/env python3
"""
Test del Sistema Optimizado
===========================

Script para probar todas las funcionalidades del sistema optimizado.
"""
import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.app.core.environment import get_settings
from src.app.core.database import init_database, create_database_engine, create_session_factory
from src.app.models.document_enhanced import Document, DocumentType, DocumentStatus
from src.app.repositories.document_repository import DocumentRepository
from src.app.services.cache import get_cache_service
cache_service = get_cache_service()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_database_connection():
    """Probar conexión a base de datos"""
    logger.info("🔄 Probando conexión a base de datos...")
    
    try:
        await init_database()
        engine = create_database_engine()
        SessionLocal = create_session_factory()
        
        # Test de conexión
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            assert result.fetchone()[0] == 1
        
        logger.info("✅ Conexión a base de datos exitosa")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error conectando a base de datos: {e}")
        return False


async def test_document_operations():
    """Probar operaciones de documentos"""
    logger.info("🔄 Probando operaciones de documentos...")
    
    try:
        SessionLocal = create_session_factory()
        db = SessionLocal()
        repository = DocumentRepository(db)
        
        # Crear documento de prueba
        test_document = await repository.create(
            filename="test_document.pdf",
            original_filename="test_document.pdf",
            file_path="/uploads/test_document.pdf",
            file_size=1024,
            mime_type="application/pdf",
            document_type=DocumentType.FACTURA.value,
            status=DocumentStatus.UPLOADED.value,
            raw_text="FACTURA N° 001-2024\nCliente: Test Client\nTotal: $100.00"
        )
        
        logger.info(f"✅ Documento creado con ID: {test_document.id}")
        
        # Probar búsqueda por ID
        found_document = await repository.get_by_id(test_document.id)
        assert found_document is not None
        assert found_document.filename == "test_document.pdf"
        logger.info("✅ Búsqueda por ID exitosa")
        
        # Probar búsqueda por tipo
        documents_by_type = await repository.get_by_type(DocumentType.FACTURA.value)
        assert len(documents_by_type) >= 1
        logger.info("✅ Búsqueda por tipo exitosa")
        
        # Probar búsqueda por texto
        search_results = await repository.search_by_text("FACTURA")
        assert len(search_results) >= 1
        logger.info("✅ Búsqueda por texto exitosa")
        
        # Probar actualización
        updated_document = await repository.update(
            test_document.id,
            confidence_score=0.95,
            status=DocumentStatus.PROCESSED.value
        )
        assert updated_document.confidence_score == 0.95
        logger.info("✅ Actualización exitosa")
        
        # Probar estadísticas
        stats = await repository.get_stats()
        assert stats['total_documents'] >= 1
        logger.info("✅ Estadísticas obtenidas exitosamente")
        
        # Limpiar documento de prueba
        await repository.delete(test_document.id)
        logger.info("✅ Documento de prueba eliminado")
        
        db.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en operaciones de documentos: {e}")
        return False


async def test_cache_system():
    """Probar sistema de cache"""
    logger.info("🔄 Probando sistema de cache...")
    
    try:
        # Test básico de cache
        test_key = "test_cache_key"
        test_value = {"message": "Hello, Cache!", "timestamp": datetime.utcnow().isoformat()}
        
        # Establecer valor
        success = await cache_service.set(test_key, test_value, ttl=60)
        assert success, "Error estableciendo valor en cache"
        logger.info("✅ Valor establecido en cache")
        
        # Obtener valor
        retrieved_value = await cache_service.get(test_key)
        assert retrieved_value is not None, "Error obteniendo valor del cache"
        assert retrieved_value["message"] == test_value["message"]
        logger.info("✅ Valor obtenido del cache")
        
        # Verificar existencia
        exists = await cache_service.exists(test_key)
        assert exists, "Error verificando existencia en cache"
        logger.info("✅ Existencia verificada en cache")
        
        # Eliminar valor
        deleted = await cache_service.delete(test_key)
        assert deleted, "Error eliminando valor del cache"
        logger.info("✅ Valor eliminado del cache")
        
        # Obtener estadísticas
        stats = await cache_service.get_stats()
        assert 'memory_cache' in stats
        assert 'redis' in stats
        logger.info("✅ Estadísticas de cache obtenidas")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en sistema de cache: {e}")
        return False


async def test_environment_configuration():
    """Probar configuración de ambiente"""
    logger.info("🔄 Probando configuración de ambiente...")
    
    try:
        settings = get_settings()
        
        # Verificar configuración básica
        assert settings.name is not None
        assert settings.version is not None
        assert settings.environment is not None
        logger.info(f"✅ Configuración básica: {settings.name} v{settings.version}")
        
        # Verificar configuración de base de datos
        assert settings.database.url is not None
        assert settings.database.url_fallback is not None
        logger.info("✅ Configuración de base de datos")
        
        # Verificar configuración de Redis
        assert settings.redis.host is not None
        assert settings.redis.port is not None
        logger.info("✅ Configuración de Redis")
        
        # Verificar configuración de OCR
        assert settings.ocr.confidence_threshold is not None
        logger.info("✅ Configuración de OCR")
        
        # Verificar configuración de LLM
        assert settings.llm.openai_model is not None
        logger.info("✅ Configuración de LLM")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en configuración de ambiente: {e}")
        return False


async def test_repository_pattern():
    """Probar patrón Repository"""
    logger.info("🔄 Probando patrón Repository...")
    
    try:
        SessionLocal = create_session_factory()
        db = SessionLocal()
        repository = DocumentRepository(db)
        
        # Test de operaciones CRUD
        documents = await repository.get_all(limit=5)
        logger.info(f"✅ Obtenidos {len(documents)} documentos")
        
        # Test de conteo
        count = await repository.count()
        logger.info(f"✅ Conteo de documentos: {count}")
        
        # Test de búsqueda avanzada
        search_results = await repository.advanced_search(
            query="test",
            limit=10
        )
        logger.info(f"✅ Búsqueda avanzada: {len(search_results)} resultados")
        
        # Test de estadísticas
        stats = await repository.get_stats()
        assert isinstance(stats, dict)
        logger.info("✅ Estadísticas del repository")
        
        db.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en patrón Repository: {e}")
        return False


async def test_schema_validation():
    """Probar validación de schemas"""
    logger.info("🔄 Probando validación de schemas...")
    
    try:
        from src.app.schemas.document_consolidated import (
            DocumentCreateSchema,
            DocumentResponseSchema,
            DocumentSearchRequestSchema
        )
        
        # Test de schema de creación
        create_data = {
            "filename": "test.pdf",
            "original_filename": "test.pdf",
            "file_path": "/uploads/test.pdf",
            "file_size": 1024,
            "mime_type": "application/pdf"
        }
        
        create_schema = DocumentCreateSchema(**create_data)
        assert create_schema.filename == "test.pdf"
        logger.info("✅ Schema de creación validado")
        
        # Test de schema de búsqueda
        search_data = {
            "query": "test",
            "page": 1,
            "size": 20
        }
        
        search_schema = DocumentSearchRequestSchema(**search_data)
        assert search_schema.query == "test"
        logger.info("✅ Schema de búsqueda validado")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en validación de schemas: {e}")
        return False


async def run_all_tests():
    """Ejecutar todas las pruebas"""
    logger.info("🚀 Iniciando pruebas del sistema optimizado...")
    
    tests = [
        ("Configuración de ambiente", test_environment_configuration),
        ("Conexión a base de datos", test_database_connection),
        ("Sistema de cache", test_cache_system),
        ("Validación de schemas", test_schema_validation),
        ("Patrón Repository", test_repository_pattern),
        ("Operaciones de documentos", test_document_operations),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 Ejecutando: {test_name}")
        try:
            if await test_func():
                passed += 1
                logger.info(f"✅ {test_name} - PASÓ")
            else:
                logger.error(f"❌ {test_name} - FALLÓ")
        except Exception as e:
            logger.error(f"❌ {test_name} - ERROR: {e}")
    
    logger.info(f"\n🎉 Pruebas completadas: {passed}/{total} pasaron")
    
    if passed == total:
        logger.info("🎉 ¡Todas las pruebas pasaron! El sistema optimizado está funcionando correctamente.")
        return True
    else:
        logger.error(f"❌ {total - passed} pruebas fallaron. Revisar logs para más detalles.")
        return False


def main():
    """Función principal"""
    try:
        success = asyncio.run(run_all_tests())
        return 0 if success else 1
    except Exception as e:
        logger.error(f"❌ Error ejecutando pruebas: {e}")
        return 1


if __name__ == "__main__":
    exit(main())















