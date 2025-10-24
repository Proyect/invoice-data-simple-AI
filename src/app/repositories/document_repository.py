"""
Document Repository
==================

Repository especializado para documentos con operaciones específicas.
"""
import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc, text
from sqlalchemy.exc import SQLAlchemyError

from .base_repository import BaseRepository
from ..models.document_unified import Document, DocumentType, DocumentStatus, OCRProvider
from ..services.cache_optimized import cached, cache_invalidate

logger = logging.getLogger(__name__)


class DocumentRepository(BaseRepository[Document]):
    """Repository especializado para documentos"""
    
    def __init__(self, db: Session):
        super().__init__(Document, db)
    
    @cached(ttl=300, key_prefix="documents_by_type")
    async def get_by_type(self, document_type: str, skip: int = 0, limit: int = 20) -> List[Document]:
        """Obtener documentos por tipo"""
        try:
            return self.db.query(Document).filter(
                Document.is_deleted == False,
                Document.document_type == document_type
            ).order_by(desc(Document.created_at)).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting documents by type {document_type}: {e}")
            raise
    
    @cached(ttl=300, key_prefix="documents_by_status")
    async def get_by_status(self, status: str, skip: int = 0, limit: int = 20) -> List[Document]:
        """Obtener documentos por estado"""
        try:
            return self.db.query(Document).filter(
                Document.is_deleted == False,
                Document.status == status
            ).order_by(desc(Document.created_at)).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting documents by status {status}: {e}")
            raise
    
    @cached(ttl=300, key_prefix="documents_needing_review")
    async def get_needing_review(self, limit: int = 20) -> List[Document]:
        """Obtener documentos que necesitan revisión"""
        try:
            return self.db.query(Document).filter(
                Document.is_deleted == False,
                or_(
                    Document.status == DocumentStatus.REVIEWING.value,
                    and_(
                        Document.confidence_score.isnot(None),
                        Document.confidence_score < 0.7
                    ),
                    Document.status == DocumentStatus.FAILED.value
                )
            ).order_by(asc(Document.priority), asc(Document.created_at)).limit(limit).all()
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting documents needing review: {e}")
            raise
    
    @cached(ttl=300, key_prefix="documents_by_user")
    async def get_by_user(self, user_id: int, skip: int = 0, limit: int = 20) -> List[Document]:
        """Obtener documentos por usuario"""
        try:
            return self.db.query(Document).filter(
                Document.is_deleted == False,
                Document.user_id == user_id
            ).order_by(desc(Document.created_at)).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting documents by user {user_id}: {e}")
            raise
    
    @cached(ttl=300, key_prefix="documents_by_organization")
    async def get_by_organization(self, organization_id: int, skip: int = 0, limit: int = 20) -> List[Document]:
        """Obtener documentos por organización"""
        try:
            return self.db.query(Document).filter(
                Document.is_deleted == False,
                Document.organization_id == organization_id
            ).order_by(desc(Document.created_at)).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting documents by organization {organization_id}: {e}")
            raise
    
    @cached(ttl=300, key_prefix="documents_search")
    async def search_by_text(self, query: str, skip: int = 0, limit: int = 20) -> List[Document]:
        """Búsqueda por texto en documentos"""
        try:
            search_conditions = or_(
                Document.filename.ilike(f"%{query}%"),
                Document.raw_text.ilike(f"%{query}%"),
                Document.original_filename.ilike(f"%{query}%")
            )
            
            return self.db.query(Document).filter(
                Document.is_deleted == False,
                search_conditions
            ).order_by(desc(Document.created_at)).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            self.logger.error(f"Error searching documents with query '{query}': {e}")
            raise
    
    @cached(ttl=300, key_prefix="documents_advanced_search")
    async def advanced_search(
        self,
        query: Optional[str] = None,
        document_type: Optional[str] = None,
        status: Optional[str] = None,
        ocr_provider: Optional[str] = None,
        min_confidence: Optional[float] = None,
        max_confidence: Optional[float] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        tags: Optional[List[str]] = None,
        organization_id: Optional[int] = None,
        user_id: Optional[int] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        skip: int = 0,
        limit: int = 20
    ) -> List[Document]:
        """Búsqueda avanzada con múltiples filtros"""
        try:
            db_query = self.db.query(Document).filter(Document.is_deleted == False)
            
            # Filtro de texto
            if query:
                text_conditions = or_(
                    Document.filename.ilike(f"%{query}%"),
                    Document.raw_text.ilike(f"%{query}%"),
                    Document.original_filename.ilike(f"%{query}%")
                )
                db_query = db_query.filter(text_conditions)
            
            # Filtro de tipo
            if document_type:
                db_query = db_query.filter(Document.document_type == document_type)
            
            # Filtro de estado
            if status:
                db_query = db_query.filter(Document.status == status)
            
            # Filtro de proveedor OCR
            if ocr_provider:
                db_query = db_query.filter(Document.ocr_provider == ocr_provider)
            
            # Filtro de confianza
            if min_confidence is not None:
                db_query = db_query.filter(Document.confidence_score >= min_confidence)
            if max_confidence is not None:
                db_query = db_query.filter(Document.confidence_score <= max_confidence)
            
            # Filtro de fechas
            if date_from:
                db_query = db_query.filter(Document.created_at >= date_from)
            if date_to:
                db_query = db_query.filter(Document.created_at <= date_to)
            
            # Filtro de tags
            if tags:
                for tag in tags:
                    db_query = db_query.filter(Document.tags.ilike(f"%{tag}%"))
            
            # Filtro de organización
            if organization_id:
                db_query = db_query.filter(Document.organization_id == organization_id)
            
            # Filtro de usuario
            if user_id:
                db_query = db_query.filter(Document.user_id == user_id)
            
            # Ordenamiento
            if hasattr(Document, sort_by):
                if sort_order.lower() == "desc":
                    db_query = db_query.order_by(desc(getattr(Document, sort_by)))
                else:
                    db_query = db_query.order_by(asc(getattr(Document, sort_by)))
            else:
                db_query = db_query.order_by(desc(Document.created_at))
            
            return db_query.offset(skip).limit(limit).all()
            
        except SQLAlchemyError as e:
            self.logger.error(f"Error in advanced search: {e}")
            raise
    
    @cached(ttl=600, key_prefix="documents_stats")
    async def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas detalladas de documentos"""
        try:
            # Estadísticas básicas
            total = self.count()
            
            # Por estado
            by_status = self.db.query(
                Document.status,
                func.count(Document.id).label('count')
            ).filter(Document.is_deleted == False).group_by(Document.status).all()
            
            # Por tipo
            by_type = self.db.query(
                Document.document_type,
                func.count(Document.id).label('count')
            ).filter(
                Document.is_deleted == False,
                Document.document_type.isnot(None)
            ).group_by(Document.document_type).all()
            
            # Por proveedor OCR
            by_ocr_provider = self.db.query(
                Document.ocr_provider,
                func.count(Document.id).label('count')
            ).filter(
                Document.is_deleted == False,
                Document.ocr_provider.isnot(None)
            ).group_by(Document.ocr_provider).all()
            
            # Por mes
            monthly_stats = self.db.query(
                func.date_trunc('month', Document.created_at).label('month'),
                func.count(Document.id).label('count')
            ).filter(Document.is_deleted == False).group_by('month').order_by('month').all()
            
            # Estadísticas de confianza
            confidence_stats = self.db.query(
                func.avg(Document.confidence_score).label('avg_confidence'),
                func.min(Document.confidence_score).label('min_confidence'),
                func.max(Document.confidence_score).label('max_confidence')
            ).filter(
                Document.is_deleted == False,
                Document.confidence_score.isnot(None)
            ).first()
            
            # Tiempo total de procesamiento
            total_processing_time = self.db.query(
                func.sum(Document.processing_time_seconds)
            ).filter(
                Document.is_deleted == False,
                Document.processing_time_seconds.isnot(None)
            ).scalar() or 0
            
            # Almacenamiento total
            total_storage = self.db.query(
                func.sum(Document.file_size)
            ).filter(
                Document.is_deleted == False,
                Document.file_size.isnot(None)
            ).scalar() or 0
            
            return {
                'total_documents': total,
                'by_status': {status: count for status, count in by_status},
                'by_type': {doc_type: count for doc_type, count in by_type},
                'by_ocr_provider': {provider: count for provider, count in by_ocr_provider},
                'by_month': {
                    month.strftime('%Y-%m'): count 
                    for month, count in monthly_stats
                },
                'average_confidence': float(confidence_stats.avg_confidence) if confidence_stats.avg_confidence else 0.0,
                'min_confidence': float(confidence_stats.min_confidence) if confidence_stats.min_confidence else 0.0,
                'max_confidence': float(confidence_stats.max_confidence) if confidence_stats.max_confidence else 0.0,
                'total_processing_time': float(total_processing_time),
                'total_storage_mb': round(total_storage / (1024 * 1024), 2) if total_storage else 0.0,
            }
            
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting document stats: {e}")
            raise
    
    @cache_invalidate("documents_*")
    async def mark_processing(self, document_id: int) -> bool:
        """Marcar documento como procesando"""
        try:
            document = self.get_by_id(document_id)
            if not document:
                return False
            
            document.status = DocumentStatus.PROCESSING.value
            self.db.commit()
            
            self.logger.info(f"Marked document {document_id} as processing")
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            self.logger.error(f"Error marking document {document_id} as processing: {e}")
            raise
    
    @cache_invalidate("documents_*")
    async def mark_processed(
        self, 
        document_id: int, 
        confidence_score: float = None,
        extracted_data: Dict[str, Any] = None,
        processing_time: float = None
    ) -> bool:
        """Marcar documento como procesado"""
        try:
            document = self.get_by_id(document_id)
            if not document:
                return False
            
            document.status = DocumentStatus.PROCESSED.value
            document.processed_at = datetime.utcnow()
            
            if confidence_score is not None:
                document.confidence_score = confidence_score
            
            if extracted_data is not None:
                document.set_extracted_data(extracted_data)
            
            if processing_time is not None:
                document.processing_time_seconds = processing_time
            
            self.db.commit()
            
            self.logger.info(f"Marked document {document_id} as processed")
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            self.logger.error(f"Error marking document {document_id} as processed: {e}")
            raise
    
    @cache_invalidate("documents_*")
    async def mark_failed(self, document_id: int, error_message: str = None) -> bool:
        """Marcar documento como fallido"""
        try:
            document = self.get_by_id(document_id)
            if not document:
                return False
            
            document.status = DocumentStatus.FAILED.value
            if error_message:
                document.review_notes = error_message
            
            self.db.commit()
            
            self.logger.info(f"Marked document {document_id} as failed")
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            self.logger.error(f"Error marking document {document_id} as failed: {e}")
            raise
    
    @cache_invalidate("documents_*")
    async def approve(self, document_id: int, reviewed_by: int, notes: str = None) -> bool:
        """Aprobar documento"""
        try:
            document = self.get_by_id(document_id)
            if not document:
                return False
            
            document.status = DocumentStatus.APPROVED.value
            document.reviewed_by = reviewed_by
            document.reviewed_at = datetime.utcnow()
            
            if notes:
                document.review_notes = notes
            
            self.db.commit()
            
            self.logger.info(f"Approved document {document_id} by user {reviewed_by}")
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            self.logger.error(f"Error approving document {document_id}: {e}")
            raise
    
    @cache_invalidate("documents_*")
    async def reject(self, document_id: int, reviewed_by: int, reason: str) -> bool:
        """Rechazar documento"""
        try:
            document = self.get_by_id(document_id)
            if not document:
                return False
            
            document.status = DocumentStatus.REJECTED.value
            document.reviewed_by = reviewed_by
            document.reviewed_at = datetime.utcnow()
            document.review_notes = reason
            
            self.db.commit()
            
            self.logger.info(f"Rejected document {document_id} by user {reviewed_by}")
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            self.logger.error(f"Error rejecting document {document_id}: {e}")
            raise
    
    @cached(ttl=300, key_prefix="documents_recent")
    async def get_recent(self, days: int = 7, limit: int = 20) -> List[Document]:
        """Obtener documentos recientes"""
        try:
            since_date = datetime.utcnow() - timedelta(days=days)
            
            return self.db.query(Document).filter(
                Document.is_deleted == False,
                Document.created_at >= since_date
            ).order_by(desc(Document.created_at)).limit(limit).all()
            
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting recent documents: {e}")
            raise
    
    @cached(ttl=300, key_prefix="documents_high_confidence")
    async def get_high_confidence(self, min_confidence: float = 0.8, limit: int = 20) -> List[Document]:
        """Obtener documentos con alta confianza"""
        try:
            return self.db.query(Document).filter(
                Document.is_deleted == False,
                Document.confidence_score >= min_confidence
            ).order_by(desc(Document.confidence_score)).limit(limit).all()
            
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting high confidence documents: {e}")
            raise
