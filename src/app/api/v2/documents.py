"""
Document Endpoints v2
=====================

Endpoints optimizados para gestión de documentos.
"""
import logging
import asyncio
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...repositories.document_repository import DocumentRepository
from ...schemas.document_consolidated import (
    DocumentResponseSchema,
    DocumentListResponseSchema,
    DocumentSearchRequestSchema,
    DocumentStatsResponseSchema,
    DocumentCreateResponseSchema,
    DocumentUpdateResponseSchema,
    DocumentDeleteResponseSchema,
    DocumentProcessingRequestSchema,
    DocumentReviewRequestSchema,
    DocumentBatchOperationRequestSchema,
    DocumentExportRequestSchema,
    ResponseSchema
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=DocumentListResponseSchema)
async def list_documents(
    skip: int = Query(0, ge=0, description="Número de documentos a omitir"),
    limit: int = Query(20, ge=1, le=100, description="Número máximo de documentos a retornar"),
    document_type: Optional[str] = Query(None, description="Filtrar por tipo de documento"),
    status: Optional[str] = Query(None, description="Filtrar por estado"),
    db: Session = Depends(get_db)
):
    """Listar documentos con filtros opcionales"""
    try:
        repository = DocumentRepository(db)
        
        if document_type or status:
            # Búsqueda con filtros
            if hasattr(repository, 'advanced_search') and callable(getattr(repository, 'advanced_search', None)):
                documents = await repository.advanced_search(
                    document_type=document_type,
                    status=status,
                    skip=skip,
                    limit=limit
                ) if asyncio.iscoroutinefunction(repository.advanced_search) else repository.advanced_search(
                    document_type=document_type,
                    status=status,
                    skip=skip,
                    limit=limit
                )
            else:
                # Búsqueda simple con filtros
                query = db.query(repository.model)
                if document_type:
                    query = query.filter(repository.model.document_type == document_type)
                if status:
                    query = query.filter(repository.model.status == status)
                documents = query.offset(skip).limit(limit).all()
            
            # Contar total
            query = db.query(repository.model)
            if document_type:
                query = query.filter(repository.model.document_type == document_type)
            if status:
                query = query.filter(repository.model.status == status)
            total = query.count()
        else:
            # Lista simple
            documents = repository.get_all(skip=skip, limit=limit)
            total = repository.count()
        
        # Calcular paginación
        total_pages = (total + limit - 1) // limit
        has_next = skip + limit < total
        has_prev = skip > 0
        
        return DocumentListResponseSchema(
            documents=[DocumentResponseSchema.model_validate(doc) for doc in documents],
            total=total,
            page=(skip // limit) + 1,
            size=limit,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev
        )
        
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")


@router.get("/{document_id}", response_model=DocumentResponseSchema)
async def get_document(
    document_id: int = Path(..., description="ID del documento"),
    db: Session = Depends(get_db)
):
    """Obtener documento por ID"""
    try:
        repository = DocumentRepository(db)
        document = await repository.get_by_id(document_id)
        
        if not document:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
        
        return DocumentResponseSchema.model_validate(document)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting document: {str(e)}")


@router.get("/search/advanced", response_model=DocumentListResponseSchema)
async def advanced_search(
    search_request: DocumentSearchRequestSchema,
    db: Session = Depends(get_db)
):
    """Búsqueda avanzada de documentos"""
    try:
        repository = DocumentRepository(db)
        
        documents = await repository.advanced_search(
            query=search_request.query,
            document_type=search_request.document_type,
            status=search_request.status,
            ocr_provider=search_request.ocr_provider,
            min_confidence=search_request.min_confidence,
            max_confidence=search_request.max_confidence,
            date_from=search_request.date_from,
            date_to=search_request.date_to,
            tags=search_request.tags,
            organization_id=search_request.organization_id,
            user_id=search_request.user_id,
            sort_by=search_request.sort_by,
            sort_order=search_request.sort_order,
            skip=(search_request.page - 1) * search_request.size,
            limit=search_request.size
        )
        
        # Contar total para paginación
        total = await repository.count(
            document_type=search_request.document_type,
            status=search_request.status,
            organization_id=search_request.organization_id,
            user_id=search_request.user_id
        )
        
        # Calcular paginación
        total_pages = (total + search_request.size - 1) // search_request.size
        has_next = search_request.page < total_pages
        has_prev = search_request.page > 1
        
        return DocumentListResponseSchema(
            documents=[DocumentResponseSchema.model_validate(doc) for doc in documents],
            total=total,
            page=search_request.page,
            size=search_request.size,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev
        )
        
    except Exception as e:
        logger.error(f"Error in advanced search: {e}")
        raise HTTPException(status_code=500, detail=f"Error in advanced search: {str(e)}")


@router.get("/stats/overview", response_model=DocumentStatsResponseSchema)
async def get_document_stats(db: Session = Depends(get_db)):
    """Obtener estadísticas de documentos"""
    try:
        repository = DocumentRepository(db)
        stats = await repository.get_stats()
        
        return DocumentStatsResponseSchema(**stats)
        
    except Exception as e:
        logger.error(f"Error getting document stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting document stats: {str(e)}")


@router.get("/needing-review/", response_model=List[DocumentResponseSchema])
async def get_documents_needing_review(
    limit: int = Query(20, ge=1, le=100, description="Número máximo de documentos"),
    db: Session = Depends(get_db)
):
    """Obtener documentos que necesitan revisión"""
    try:
        repository = DocumentRepository(db)
        documents = await repository.get_needing_review(limit=limit)
        
        return [DocumentResponseSchema.model_validate(doc) for doc in documents]
        
    except Exception as e:
        logger.error(f"Error getting documents needing review: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting documents needing review: {str(e)}")


@router.get("/by-type/{document_type}", response_model=List[DocumentResponseSchema])
async def get_documents_by_type(
    document_type: str = Path(..., description="Tipo de documento"),
    skip: int = Query(0, ge=0, description="Número de documentos a omitir"),
    limit: int = Query(20, ge=1, le=100, description="Número máximo de documentos"),
    db: Session = Depends(get_db)
):
    """Obtener documentos por tipo"""
    try:
        repository = DocumentRepository(db)
        documents = await repository.get_by_type(
            document_type=document_type,
            skip=skip,
            limit=limit
        )
        
        return [DocumentResponseSchema.model_validate(doc) for doc in documents]
        
    except Exception as e:
        logger.error(f"Error getting documents by type {document_type}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting documents by type: {str(e)}")


@router.get("/by-status/{status}", response_model=List[DocumentResponseSchema])
async def get_documents_by_status(
    status: str = Path(..., description="Estado del documento"),
    skip: int = Query(0, ge=0, description="Número de documentos a omitir"),
    limit: int = Query(20, ge=1, le=100, description="Número máximo de documentos"),
    db: Session = Depends(get_db)
):
    """Obtener documentos por estado"""
    try:
        repository = DocumentRepository(db)
        documents = await repository.get_by_status(
            status=status,
            skip=skip,
            limit=limit
        )
        
        return [DocumentResponseSchema.model_validate(doc) for doc in documents]
        
    except Exception as e:
        logger.error(f"Error getting documents by status {status}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting documents by status: {str(e)}")


@router.get("/search/text", response_model=List[DocumentResponseSchema])
async def search_documents_by_text(
    query: str = Query(..., description="Consulta de búsqueda"),
    skip: int = Query(0, ge=0, description="Número de documentos a omitir"),
    limit: int = Query(20, ge=1, le=100, description="Número máximo de documentos"),
    db: Session = Depends(get_db)
):
    """Búsqueda de documentos por texto"""
    try:
        repository = DocumentRepository(db)
        documents = await repository.search_by_text(
            query=query,
            skip=skip,
            limit=limit
        )
        
        return [DocumentResponseSchema.model_validate(doc) for doc in documents]
        
    except Exception as e:
        logger.error(f"Error searching documents with query '{query}': {e}")
        raise HTTPException(status_code=500, detail=f"Error searching documents: {str(e)}")


@router.get("/recent/", response_model=List[DocumentResponseSchema])
async def get_recent_documents(
    days: int = Query(7, ge=1, le=30, description="Número de días hacia atrás"),
    limit: int = Query(20, ge=1, le=100, description="Número máximo de documentos"),
    db: Session = Depends(get_db)
):
    """Obtener documentos recientes"""
    try:
        repository = DocumentRepository(db)
        documents = await repository.get_recent(days=days, limit=limit)
        
        return [DocumentResponseSchema.model_validate(doc) for doc in documents]
        
    except Exception as e:
        logger.error(f"Error getting recent documents: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting recent documents: {str(e)}")


@router.get("/high-confidence/", response_model=List[DocumentResponseSchema])
async def get_high_confidence_documents(
    min_confidence: float = Query(0.8, ge=0.0, le=1.0, description="Confianza mínima"),
    limit: int = Query(20, ge=1, le=100, description="Número máximo de documentos"),
    db: Session = Depends(get_db)
):
    """Obtener documentos con alta confianza"""
    try:
        repository = DocumentRepository(db)
        documents = await repository.get_high_confidence(
            min_confidence=min_confidence,
            limit=limit
        )
        
        return [DocumentResponseSchema.model_validate(doc) for doc in documents]
        
    except Exception as e:
        logger.error(f"Error getting high confidence documents: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting high confidence documents: {str(e)}")
