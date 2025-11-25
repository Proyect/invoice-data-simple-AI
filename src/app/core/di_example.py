"""
Ejemplo de uso de Dependency Injection
=======================================

Este archivo muestra cómo usar el sistema de DI en diferentes escenarios.
"""
from fastapi import Depends
from sqlalchemy.orm import Session

from .dependencies import (
    get_afip_invoice_extraction_service,
    get_optimal_ocr_service,
    get_intelligent_extraction_service,
    get_async_processing_service,
    get_document_repository,
    get_db
)


# ============================================================================
# Ejemplo 1: Uso básico en endpoint
# ============================================================================

async def example_endpoint(
    db: Session = Depends(get_db),
    afip_service = Depends(get_afip_invoice_extraction_service),
    ocr_service = Depends(get_optimal_ocr_service)
):
    """
    Ejemplo de endpoint usando DI.
    FastAPI inyecta automáticamente las dependencias.
    """
    # Usar servicios inyectados
    text = ocr_service.extract_text("path/to/image.jpg")
    invoice_data = afip_service.extract_afip_invoice_data(text)
    
    return {"invoice_data": invoice_data}


# ============================================================================
# Ejemplo 2: Uso con múltiples dependencias
# ============================================================================

async def example_complex_endpoint(
    db: Session = Depends(get_db),
    processing_service = Depends(get_async_processing_service),
    document_repo = Depends(get_document_repository)
):
    """
    Ejemplo con servicios que tienen dependencias anidadas.
    FastAPI resuelve automáticamente el árbol de dependencias.
    """
    # processing_service ya tiene ocr_service y extraction_service inyectados
    job_id = await processing_service.process_document_async("path/to/doc.pdf")
    
    # document_repo ya tiene la sesión de DB inyectada
    documents = await document_repo.get_all(skip=0, limit=10)
    
    return {"job_id": job_id, "documents": documents}


# ============================================================================
# Ejemplo 3: Testing con mocks
# ============================================================================

def test_with_mocks():
    """
    Ejemplo de cómo testear con mocks usando DI.
    """
    from unittest.mock import Mock
    
    # Crear mocks
    mock_ocr = Mock()
    mock_ocr.extract_text.return_value = "Texto extraído"
    
    mock_extraction = Mock()
    mock_extraction.extract_intelligent_data.return_value = {
        "document_type": "factura",
        "confidence": 0.9
    }
    
    # Crear servicio con mocks inyectados
    from ..services.async_processing_service import AsyncProcessingService
    service = AsyncProcessingService(
        ocr_service=mock_ocr,
        extraction_service=mock_extraction
    )
    
    # Ahora puedes testear sin dependencias reales
    result = service._process_document_worker("test.jpg", "factura", 1)
    assert result is not None


# ============================================================================
# Ejemplo 4: Uso del Container (opcional)
# ============================================================================

def example_with_container():
    """
    Ejemplo usando el DependencyContainer para casos avanzados.
    """
    from .dependencies import get_container
    
    container = get_container()
    
    # Obtener servicios del container
    afip_service = container.get('afip_invoice_extraction')
    ocr_service = container.get('optimal_ocr')
    
    # Usar servicios
    text = ocr_service.extract_text("path/to/image.jpg")
    invoice_data = afip_service.extract_afip_invoice_data(text)
    
    return invoice_data

