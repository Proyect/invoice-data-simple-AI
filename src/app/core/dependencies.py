"""
Sistema de Dependency Injection
===============================

Sistema centralizado de inyección de dependencias para mejorar
testabilidad y desacoplamiento del código.
"""
import logging
from typing import Optional
from functools import lru_cache

from fastapi import Depends
from sqlalchemy.orm import Session

from .database import SessionLocal, get_db
from .config import settings

logger = logging.getLogger(__name__)


# ============================================================================
# Providers de Servicios
# ============================================================================

@lru_cache()
def get_afip_validation_service():
    """Provider para AFIPValidationService"""
    from ..services.afip_validation_service import AFIPValidationService
    return AFIPValidationService()


@lru_cache()
def get_specialized_ocr_service():
    """Provider para SpecializedOCRService"""
    from ..services.specialized_ocr_service import SpecializedOCRService
    return SpecializedOCRService()


@lru_cache()
def get_universal_validation_service():
    """Provider para UniversalValidationService"""
    from ..services.universal_validation_service import UniversalValidationService
    return UniversalValidationService()


@lru_cache()
def get_optimal_ocr_service():
    """Provider para OptimalOCRService"""
    from ..services.optimal_ocr_service import OptimalOCRService
    return OptimalOCRService()


@lru_cache()
def get_intelligent_extraction_service():
    """Provider para IntelligentExtractionService"""
    from ..services.intelligent_extraction_service import IntelligentExtractionService
    return IntelligentExtractionService()


@lru_cache()
def get_afip_invoice_extraction_service(
    validation_service = Depends(get_afip_validation_service),
    specialized_ocr = Depends(get_specialized_ocr_service),
    universal_validation = Depends(get_universal_validation_service)
):
    """Provider para AFIPInvoiceExtractionService con dependencias inyectadas"""
    from ..services.afip_invoice_extraction_service import AFIPInvoiceExtractionService
    return AFIPInvoiceExtractionService(
        validation_service=validation_service,
        specialized_ocr=specialized_ocr,
        universal_validation=universal_validation
    )


@lru_cache()
def get_basic_extraction_service():
    """Provider para BasicExtractionService"""
    from ..services.basic_extraction_service import BasicExtractionService
    return BasicExtractionService()


@lru_cache()
def get_dni_extraction_service():
    """Provider para DNIExtractionService"""
    from ..services.dni_extraction_service import DNIExtractionService
    return DNIExtractionService()


@lru_cache()
def get_academic_document_extraction_service():
    """Provider para AcademicDocumentExtractionService"""
    from ..services.academic_document_extraction_service import AcademicDocumentExtractionService
    return AcademicDocumentExtractionService()


@lru_cache()
def get_cache_service():
    """Provider para CacheService"""
    from ..services.cache_service import CacheService
    return CacheService()


def get_async_processing_service(
    ocr_service = Depends(get_optimal_ocr_service),
    extraction_service = Depends(get_intelligent_extraction_service)
):
    """Provider para AsyncProcessingService con dependencias inyectadas"""
    from ..services.async_processing_service import AsyncProcessingService
    return AsyncProcessingService(
        ocr_service=ocr_service,
        extraction_service=extraction_service
    )


@lru_cache()
def get_document_repository(db: Session = Depends(get_db)):
    """Provider para DocumentRepository"""
    from ..repositories.document_repository import DocumentRepository
    return DocumentRepository(db)


# ============================================================================
# Container de Dependencias (opcional, para casos avanzados)
# ============================================================================

class DependencyContainer:
    """
    Container centralizado de dependencias.
    Útil para casos donde necesitas más control sobre el ciclo de vida.
    """
    
    def __init__(self):
        self._services = {}
        self._initialized = False
    
    def initialize(self):
        """Inicializar todas las dependencias"""
        if self._initialized:
            return
        
        logger.info("Inicializando Dependency Container...")
        
        # Servicios base
        self._services['afip_validation'] = get_afip_validation_service()
        self._services['specialized_ocr'] = get_specialized_ocr_service()
        self._services['universal_validation'] = get_universal_validation_service()
        self._services['optimal_ocr'] = get_optimal_ocr_service()
        self._services['intelligent_extraction'] = get_intelligent_extraction_service()
        self._services['cache'] = get_cache_service()
        
        # Servicios compuestos
        self._services['afip_invoice_extraction'] = get_afip_invoice_extraction_service(
            validation_service=self._services['afip_validation'],
            specialized_ocr=self._services['specialized_ocr'],
            universal_validation=self._services['universal_validation']
        )
        
        self._services['async_processing'] = get_async_processing_service(
            ocr_service=self._services['optimal_ocr'],
            extraction_service=self._services['intelligent_extraction']
        )
        
        self._initialized = True
        logger.info("✅ Dependency Container inicializado")
    
    def get(self, service_name: str):
        """Obtener un servicio del container"""
        if not self._initialized:
            self.initialize()
        return self._services.get(service_name)
    
    def register(self, service_name: str, service_instance):
        """Registrar un servicio manualmente (útil para testing)"""
        self._services[service_name] = service_instance
    
    def clear(self):
        """Limpiar el container (útil para testing)"""
        self._services.clear()
        self._initialized = False


# Instancia global del container (opcional)
_container: Optional[DependencyContainer] = None


def get_container() -> DependencyContainer:
    """Obtener la instancia global del container"""
    global _container
    if _container is None:
        _container = DependencyContainer()
        _container.initialize()
    return _container


def reset_container():
    """Resetear el container (útil para testing)"""
    global _container
    _container = None

