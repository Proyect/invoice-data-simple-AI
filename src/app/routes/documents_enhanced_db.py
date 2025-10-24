"""
Rutas para documentos mejorados con conexión a base de datos
"""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from ..core.database import get_db
from ..models.document import Document
from ..models.user import User
from ..schemas.document_enhanced import (
    DocumentEnhancedCreate,
    DocumentEnhancedUpdate,
    DocumentEnhancedResponse,
    DocumentEnhancedListResponse,
    DocumentSearchRequest,
    DocumentStatsResponse
)

logger = logging.getLogger(__name__)

# Crear router
router = APIRouter()

@router.get("/", response_model=DocumentEnhancedListResponse, summary="Listar documentos mejorados")
async def list_documents_enhanced(
    page: int = 1,
    size: int = 10,
    document_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Listar documentos con funcionalidades mejoradas
    """
    try:
        # Consulta base
        query = db.query(Document)
        
        # Aplicar filtros
        if document_type:
            query = query.filter(Document.document_type == document_type)
        if status:
            query = query.filter(Document.status == status)
        
        # Paginación
        offset = (page - 1) * size
        total = query.count()
        documents = query.offset(offset).limit(size).all()
        
        return DocumentEnhancedListResponse(
            items=[DocumentEnhancedResponse.from_orm(doc) for doc in documents],
            total=total,
            page=page,
            size=size,
            total_pages=(total + size - 1) // size
        )
        
    except Exception as e:
        logger.error(f"Error listando documentos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.post("/", response_model=DocumentEnhancedResponse, summary="Crear documento mejorado")
async def create_document_enhanced(
    document_data: DocumentEnhancedCreate,
    db: Session = Depends(get_db)
):
    """
    Crear un nuevo documento con funcionalidades mejoradas
    """
    try:
        # Crear documento
        document = Document(
            filename=document_data.filename,
            document_type=document_data.document_type,
            status=document_data.status,
            confidence_score=document_data.confidence_score,
            extracted_data=document_data.extracted_data,
            metadata=document_data.metadata
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        return DocumentEnhancedResponse.from_orm(document)
        
    except Exception as e:
        logger.error(f"Error creando documento: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creando documento"
        )

@router.get("/{document_id}", response_model=DocumentEnhancedResponse, summary="Obtener documento mejorado")
async def get_document_enhanced(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener un documento específico con funcionalidades mejoradas
    """
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Documento no encontrado"
            )
        
        return DocumentEnhancedResponse.from_orm(document)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo documento: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.put("/{document_id}", response_model=DocumentEnhancedResponse, summary="Actualizar documento mejorado")
async def update_document_enhanced(
    document_id: int,
    update_data: DocumentEnhancedUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualizar documento con funcionalidades mejoradas
    """
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Documento no encontrado"
            )
        
        # Actualizar campos
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(document, field, value)
        
        db.commit()
        db.refresh(document)
        
        return DocumentEnhancedResponse.from_orm(document)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando documento: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error actualizando documento"
        )

@router.delete("/{document_id}", summary="Eliminar documento mejorado")
async def delete_document_enhanced(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Eliminar documento con funcionalidades mejoradas
    """
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Documento no encontrado"
            )
        
        db.delete(document)
        db.commit()
        
        return {"message": "Documento eliminado exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error eliminando documento: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error eliminando documento"
        )

@router.post("/search", response_model=DocumentEnhancedListResponse, summary="Búsqueda avanzada de documentos")
async def search_documents_enhanced(
    search_request: DocumentSearchRequest,
    db: Session = Depends(get_db)
):
    """
    Búsqueda avanzada con múltiples criterios
    """
    try:
        query = db.query(Document)
        
        # Aplicar filtros de búsqueda
        if search_request.query:
            query = query.filter(Document.filename.contains(search_request.query))
        
        if search_request.document_type:
            query = query.filter(Document.document_type == search_request.document_type)
        
        if search_request.status:
            query = query.filter(Document.status == search_request.status)
        
        if search_request.date_from:
            query = query.filter(Document.created_at >= search_request.date_from)
        
        if search_request.date_to:
            query = query.filter(Document.created_at <= search_request.date_to)
        
        # Paginación
        offset = (search_request.page - 1) * search_request.size
        total = query.count()
        documents = query.offset(offset).limit(search_request.size).all()
        
        return DocumentEnhancedListResponse(
            items=[DocumentEnhancedResponse.from_orm(doc) for doc in documents],
            total=total,
            page=search_request.page,
            size=search_request.size,
            total_pages=(total + search_request.size - 1) // search_request.size
        )
        
    except Exception as e:
        logger.error(f"Error en búsqueda: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error en búsqueda"
        )

@router.get("/stats/overview", response_model=DocumentStatsResponse, summary="Estadísticas mejoradas")
async def get_documents_stats_enhanced(db: Session = Depends(get_db)):
    """
    Obtener estadísticas mejoradas de documentos
    """
    try:
        total_documents = db.query(Document).count()
        processed_documents = db.query(Document).filter(Document.status == "processed").count()
        pending_documents = db.query(Document).filter(Document.status == "pending").count()
        failed_documents = db.query(Document).filter(Document.status == "failed").count()
        
        # Calcular promedio de confianza
        avg_confidence = db.query(Document).filter(
            Document.confidence_score.isnot(None)
        ).with_entities(Document.confidence_score).all()
        
        avg_confidence_score = 0.0
        if avg_confidence:
            avg_confidence_score = sum([c[0] for c in avg_confidence if c[0]]) / len(avg_confidence)
        
        return DocumentStatsResponse(
            total_documents=total_documents,
            processed_documents=processed_documents,
            pending_documents=pending_documents,
            failed_documents=failed_documents,
            average_confidence=avg_confidence_score,
            processing_time_avg=0.0  # TODO: Implementar cálculo real
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error obteniendo estadísticas"
        )

# Endpoints adicionales para funcionalidad completa
@router.post("/{document_id}/process", summary="Procesar documento mejorado")
async def process_document_enhanced(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Procesar documento con funcionalidades mejoradas"""
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Documento no encontrado"
            )
        
        # Simular procesamiento
        document.status = "processed"
        document.confidence_score = 0.95
        
        db.commit()
        db.refresh(document)
        
        return {
            "message": f"Documento {document_id} procesado exitosamente",
            "document_id": document_id,
            "processing_id": f"proc_{document_id}",
            "status": "completed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error procesando documento: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error procesando documento"
        )

@router.post("/batch", summary="Operaciones en lote")
async def batch_operations_enhanced(
    document_ids: List[int],
    operation: str,
    db: Session = Depends(get_db)
):
    """Operaciones en lote con funcionalidades mejoradas"""
    try:
        documents = db.query(Document).filter(Document.id.in_(document_ids)).all()
        
        processed_count = 0
        for document in documents:
            if operation == "delete":
                db.delete(document)
                processed_count += 1
            elif operation == "process":
                document.status = "processed"
                processed_count += 1
        
        db.commit()
        
        return {
            "message": "Operaciones en lote completadas",
            "operation": operation,
            "processed_count": processed_count,
            "status": "completed"
        }
        
    except Exception as e:
        logger.error(f"Error en operaciones en lote: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error en operaciones en lote"
        )
