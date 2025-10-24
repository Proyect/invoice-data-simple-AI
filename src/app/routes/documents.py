from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, text, or_
import os
from typing import List, Optional
from ..core.database import get_db
from ..models.document import Document
from ..schemas.document import DocumentResponse, DocumentListResponse
from ..services.cache_service import cache_service
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(
    skip: int = Query(0, ge=0, description="Número de documentos a omitir"),
    limit: int = Query(10, ge=1, le=100, description="Número máximo de documentos a retornar"),
    search: Optional[str] = Query(None, description="Búsqueda en texto completo"),
    db: Session = Depends(get_db)
):
    """
    Lista documentos con búsqueda full-text y cache
    """
    try:
        # Crear clave de cache
        cache_key = f"documents:{skip}:{limit}:{search or 'all'}"
        
        # Intentar obtener del cache
        cached_result = await cache_service.get(cache_key)
        if cached_result:
            return DocumentListResponse(**cached_result)
        
        # Query base
        query = db.query(Document)
        
        # Aplicar búsqueda si se proporciona
        if search:
            # Búsqueda simple compatible con SQLite
            search_filter = or_(
                Document.filename.ilike(f"%{search}%"),
                Document.raw_text.ilike(f"%{search}%"),
                Document.original_filename.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        # Obtener total
        total = query.count()
        
        # Aplicar paginación y ordenamiento
        documents = query.order_by(Document.created_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()
        
        result = DocumentListResponse(
            documents=[DocumentResponse.from_orm(doc) for doc in documents],
            total=total,
            page=(skip // limit) + 1,
            size=limit
        )
        
        # Guardar en cache por 5 minutos
        await cache_service.set(cache_key, result.dict(), 300)
        
        return result
        
    except Exception as e:
        logger.error(f"Error listando documentos: {e}")
        raise HTTPException(status_code=500, detail=f"Error listando documentos: {str(e)}")

@router.get("/documents/search")
async def search_documents(
    q: str = Query(..., description="Consulta de búsqueda"),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Búsqueda avanzada con ranking de relevancia.
    - Usa búsqueda full-text en PostgreSQL.
    - En SQLite, hace un fallback seguro a LIKE/ILIKE.
    """
    try:
        dialect = getattr(getattr(db, "bind", None), "dialect", None)
        dialect_name = getattr(dialect, "name", "") if dialect else ""

        if dialect_name == "postgresql":
            # Búsqueda avanzada con ranking en PostgreSQL
            query = text(
                """
                SELECT d.*, ts_rank(d.search_vector, plainto_tsquery('spanish', :query)) as rank
                FROM documents d
                WHERE d.search_vector @@ plainto_tsquery('spanish', :query)
                ORDER BY rank DESC
                LIMIT :limit
                """
            )
            result = db.execute(query, {"query": q, "limit": limit})
            documents = result.fetchall()
            results = [
                {
                    "id": doc.id,
                    "filename": doc.filename,
                    "rank": float(doc.rank),
                    "created_at": doc.created_at,
                    "confidence_score": doc.confidence_score,
                }
                for doc in documents
            ]
        else:
            # Fallback para SQLite u otros motores sin full-text
            base_query = (
                db.query(Document)
                .filter(
                    or_(
                        Document.filename.ilike(f"%{q}%"),
                        Document.raw_text.ilike(f"%{q}%"),
                    )
                )
                .order_by(Document.created_at.desc())
                .limit(limit)
            )
            docs = base_query.all()
            results = [
                {
                    "id": d.id,
                    "filename": d.filename,
                    "rank": 0.0,
                    "created_at": d.created_at,
                    "confidence_score": d.confidence_score,
                }
                for d in docs
            ]

        return {"query": q, "results": results, "total": len(results)}

    except Exception as e:
        logger.error(f"Error en búsqueda: {e}")
        # Devolver vacío pero sin 500 para mayor robustez
        return {"query": q, "results": [], "total": 0}

@router.get("/documents/stats")
async def get_document_stats(db: Session = Depends(get_db)):
    """
    Estadísticas de documentos con cache y compatibilidad con SQLite.
    """
    cache_key = "document_stats"

    # Intentar obtener del cache
    cached_stats = await cache_service.get(cache_key)
    if cached_stats:
        return cached_stats

    try:
        # Estadísticas básicas
        total_docs = db.query(Document).count()

        # Por tipo de archivo
        mime_stats = (
            db.query(Document.mime_type, func.count(Document.id).label("count"))
            .group_by(Document.mime_type)
            .all()
        )

        # Por mes (PostgreSQL vs SQLite)
        dialect = getattr(getattr(db, "bind", None), "dialect", None)
        dialect_name = getattr(dialect, "name", "") if dialect else ""
        if dialect_name == "postgresql":
            monthly_stats = (
                db.query(
                    func.date_trunc("month", Document.created_at).label("month"),
                    func.count(Document.id).label("count"),
                )
                .group_by("month")
                .order_by("month")
                .all()
            )
            by_month = [
                {"month": month.strftime("%Y-%m"), "count": count}
                for month, count in monthly_stats
            ]
        else:
            # SQLite: usar strftime para obtener YYYY-MM
            monthly_stats = (
                db.query(
                    func.strftime("%Y-%m", Document.created_at).label("month"),
                    func.count(Document.id).label("count"),
                )
                .group_by("month")
                .order_by("month")
                .all()
            )
            by_month = [{"month": month, "count": count} for month, count in monthly_stats]

        # Confianza promedio
        avg_confidence = db.query(func.avg(Document.confidence_score)).scalar()

        # Por proveedor OCR
        ocr_stats = (
            db.query(Document.ocr_provider, func.count(Document.id).label("count"))
            .group_by(Document.ocr_provider)
            .all()
        )

        stats = {
            "total_documents": total_docs,
            "by_mime_type": [
                {"mime_type": mime_type, "count": count} for mime_type, count in mime_stats
            ],
            "by_month": by_month,
            "by_ocr_provider": [
                {"provider": provider, "count": count} for provider, count in ocr_stats
            ],
            "average_confidence": float(avg_confidence) if avg_confidence else 0,
        }

        # Guardar en cache por 1 hora
        await cache_service.set(cache_key, stats, 3600)

        return stats

    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        # Responder vacío pero sin 500 en entornos sin funciones SQL avanzadas
        return {
            "total_documents": 0,
            "by_mime_type": [],
            "by_month": [],
            "by_ocr_provider": [],
            "average_confidence": 0.0,
        }

@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene un documento específico por ID
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    
    return DocumentResponse.from_orm(document)

@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Elimina un documento y su archivo asociado
    """
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
        
        # Eliminar archivo físico si existe
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        # Eliminar de base de datos
        db.delete(document)
        db.commit()
        
        # Invalidar cache relacionado
        await cache_service.invalidate_pattern("documents:*")
        await cache_service.invalidate_pattern("document_stats")
        
        return {"detail": "Documento eliminado correctamente"}
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error eliminando documento: {e}")
        raise HTTPException(status_code=500, detail=f"Error eliminando documento: {str(e)}")

@router.get("/documents/{document_id}/text")
async def get_document_text(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene solo el texto extraído de un documento
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    
    return {
        "document_id": document_id,
        "filename": document.filename,
        "raw_text": document.raw_text,
        "confidence_score": document.confidence_score,
        "ocr_provider": document.ocr_provider,
        "processing_time": document.processing_time
    }

@router.get("/documents/{document_id}/data")
async def get_document_data(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene solo los datos extraídos de un documento
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    
    return {
        "document_id": document_id,
        "filename": document.filename,
        "extracted_data": document.extracted_data,
        "confidence_score": document.confidence_score,
        "document_type": document.extracted_data.get('document_type') if document.extracted_data else None
    }

@router.post("/documents/{document_id}/reprocess")
async def reprocess_document(
    document_id: int,
    document_type: Optional[str] = Query(None, description="Nuevo tipo de documento"),
    db: Session = Depends(get_db)
):
    """
    Reprocesa un documento existente
    """
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
        
        # Verificar que el archivo existe
        if not os.path.exists(document.file_path):
            raise HTTPException(status_code=404, detail="Archivo no encontrado")
        
        # Iniciar reprocesamiento asíncrono
        processing_service = AsyncProcessingService()
        job_id = await processing_service.process_document_async(
            document.file_path, 
            document_type or "desconocido", 
            document_id
        )
        
        return {
            "message": "Reprocesamiento iniciado",
            "document_id": document_id,
            "job_id": job_id,
            "status_url": f"/api/v1/jobs/{job_id}/status"
        }
        
    except Exception as e:
        logger.error(f"Error reprocesando documento: {e}")
        raise HTTPException(status_code=500, detail=f"Error reprocesando documento: {str(e)}")
