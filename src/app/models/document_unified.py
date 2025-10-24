"""
Modelo Unificado de Documentos
==============================

Modelo único que combina funcionalidades de Document y DocumentEnhanced.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, Index, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql import func

from .base import BaseModel, TimestampMixin, SoftDeleteMixin, MetadataMixin, SearchableMixin


class DocumentType(str, Enum):
    """Tipos de documentos soportados"""
    FACTURA = "factura"
    RECIBO = "recibo"
    CONTRATO = "contrato"
    FORMULARIO = "formulario"
    CEDULA = "cedula"
    PASAPORTE = "pasaporte"
    LICENCIA = "licencia"
    CERTIFICADO = "certificado"
    OTRO = "otro"


class DocumentStatus(str, Enum):
    """Estados del procesamiento del documento"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    REVIEWING = "reviewing"
    APPROVED = "approved"
    REJECTED = "rejected"


class OCRProvider(str, Enum):
    """Proveedores de OCR disponibles"""
    TESSERACT = "tesseract"
    GOOGLE_VISION = "google_vision"
    AWS_TEXTRACT = "aws_textract"
    AZURE_OCR = "azure_ocr"
    HYBRID = "hybrid"


class ExtractionMethod(str, Enum):
    """Métodos de extracción de datos"""
    REGEX = "regex"
    SPACY = "spacy"
    LLM = "llm"
    HYBRID = "hybrid"
    MANUAL = "manual"


class Document(BaseModel, TimestampMixin, SoftDeleteMixin, MetadataMixin, SearchableMixin):
    """Modelo unificado de documentos"""
    __tablename__ = "documents"
    
    # Información del archivo
    filename = Column(String(255), nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True, index=True)
    
    # Clasificación del documento
    document_type = Column(String(50), nullable=True, index=True)  # DocumentType
    status = Column(String(50), nullable=False, default=DocumentStatus.UPLOADED.value, index=True)  # DocumentStatus
    priority = Column(Integer, default=5, nullable=False)  # 1=alta, 10=baja
    language = Column(String(10), default="es", nullable=False)
    
    # Datos extraídos
    raw_text = Column(Text, nullable=True)
    extracted_data = Column(Text, nullable=True)  # JSON como texto para compatibilidad
    confidence_score = Column(Float, nullable=True, index=True)  # 0.0 - 1.0
    quality_score = Column(Float, nullable=True)  # 0.0 - 1.0
    
    # Información de procesamiento
    ocr_provider = Column(String(50), nullable=True, index=True)  # OCRProvider
    extraction_method = Column(String(50), nullable=True)  # ExtractionMethod
    ocr_cost = Column(Float, nullable=True, default=0.0)
    processing_time_seconds = Column(Float, nullable=True)
    
    # Metadatos adicionales
    page_count = Column(Integer, nullable=True)
    word_count = Column(Integer, nullable=True)
    review_notes = Column(Text, nullable=True)
    tags = Column(Text, nullable=True)  # JSON array como texto
    
    # Relaciones
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True, index=True)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timestamps adicionales
    processed_at = Column(DateTime(timezone=True), nullable=True, index=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Índices compuestos
    __table_args__ = (
        Index('ix_documents_type_status', 'document_type', 'status'),
        Index('ix_documents_created_status', 'created_at', 'status'),
        Index('ix_documents_user_created', 'user_id', 'created_at'),
        Index('ix_documents_org_created', 'organization_id', 'created_at'),
        Index('ix_documents_confidence_type', 'confidence_score', 'document_type'),
    )
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.filename}', type='{self.document_type}', status='{self.status}')>"
    
    # Propiedades calculadas
    @property
    def file_size_mb(self) -> Optional[float]:
        """Tamaño del archivo en MB"""
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return None
    
    @property
    def is_processed(self) -> bool:
        """Indica si el documento fue procesado"""
        return self.status in [DocumentStatus.PROCESSED.value, DocumentStatus.APPROVED.value]
    
    @property
    def needs_review(self) -> bool:
        """Indica si necesita revisión manual"""
        return (
            self.status == DocumentStatus.REVIEWING.value or
            (self.confidence_score is not None and self.confidence_score < 0.7) or
            self.status == DocumentStatus.FAILED.value
        )
    
    # Métodos para manejo de datos JSON
    def get_extracted_data(self) -> Dict[str, Any]:
        """Obtener datos extraídos como diccionario"""
        if self.extracted_data:
            import json
            return json.loads(self.extracted_data)
        return {}
    
    def set_extracted_data(self, data: Dict[str, Any]) -> None:
        """Establecer datos extraídos"""
        import json
        self.extracted_data = json.dumps(data)
    
    def get_tags(self) -> List[str]:
        """Obtener tags como lista"""
        if self.tags:
            import json
            return json.loads(self.tags)
        return []
    
    def set_tags(self, tags: List[str]) -> None:
        """Establecer tags"""
        import json
        self.tags = json.dumps(tags)
    
    def add_tag(self, tag: str) -> None:
        """Agregar un tag"""
        current_tags = self.get_tags()
        if tag not in current_tags:
            current_tags.append(tag)
            self.set_tags(current_tags)
    
    def remove_tag(self, tag: str) -> None:
        """Remover un tag"""
        current_tags = self.get_tags()
        if tag in current_tags:
            current_tags.remove(tag)
            self.set_tags(current_tags)
    
    # Métodos de estado
    def mark_processing(self, session: Session) -> None:
        """Marcar como procesando"""
        self.status = DocumentStatus.PROCESSING.value
        session.commit()
    
    def mark_processed(self, session: Session, confidence_score: float = None) -> None:
        """Marcar como procesado"""
        self.status = DocumentStatus.PROCESSED.value
        self.processed_at = datetime.utcnow()
        if confidence_score is not None:
            self.confidence_score = confidence_score
        session.commit()
    
    def mark_failed(self, session: Session, error_message: str = None) -> None:
        """Marcar como fallido"""
        self.status = DocumentStatus.FAILED.value
        if error_message:
            self.review_notes = error_message
        session.commit()
    
    def mark_for_review(self, session: Session, reason: str = None) -> None:
        """Marcar para revisión"""
        self.status = DocumentStatus.REVIEWING.value
        if reason:
            self.review_notes = reason
        session.commit()
    
    def approve(self, session: Session, reviewed_by: int, notes: str = None) -> None:
        """Aprobar documento"""
        self.status = DocumentStatus.APPROVED.value
        self.reviewed_by = reviewed_by
        self.reviewed_at = datetime.utcnow()
        if notes:
            self.review_notes = notes
        session.commit()
    
    def reject(self, session: Session, reviewed_by: int, reason: str) -> None:
        """Rechazar documento"""
        self.status = DocumentStatus.REJECTED.value
        self.reviewed_by = reviewed_by
        self.reviewed_at = datetime.utcnow()
        self.review_notes = reason
        session.commit()
    
    # Métodos de búsqueda
    @classmethod
    def search_by_text(cls, session: Session, query: str, limit: int = 20) -> List['Document']:
        """Búsqueda por texto"""
        return session.query(cls).filter(
            cls.is_deleted == False,
            cls.raw_text.ilike(f"%{query}%")
        ).limit(limit).all()
    
    @classmethod
    def get_by_type(cls, session: Session, document_type: str, limit: int = 20) -> List['Document']:
        """Obtener por tipo de documento"""
        return session.query(cls).filter(
            cls.is_deleted == False,
            cls.document_type == document_type
        ).order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_by_status(cls, session: Session, status: str, limit: int = 20) -> List['Document']:
        """Obtener por estado"""
        return session.query(cls).filter(
            cls.is_deleted == False,
            cls.status == status
        ).order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_needing_review(cls, session: Session, limit: int = 20) -> List['Document']:
        """Obtener documentos que necesitan revisión"""
        return session.query(cls).filter(
            cls.is_deleted == False,
            cls.status == DocumentStatus.REVIEWING.value
        ).order_by(cls.priority.asc(), cls.created_at.asc()).limit(limit).all()
    
    @classmethod
    def get_stats(cls, session: Session) -> Dict[str, Any]:
        """Obtener estadísticas de documentos"""
        from sqlalchemy import func
        
        total = session.query(cls).filter(cls.is_deleted == False).count()
        
        by_status = session.query(
            cls.status,
            func.count(cls.id).label('count')
        ).filter(cls.is_deleted == False).group_by(cls.status).all()
        
        by_type = session.query(
            cls.document_type,
            func.count(cls.id).label('count')
        ).filter(
            cls.is_deleted == False,
            cls.document_type.isnot(None)
        ).group_by(cls.document_type).all()
        
        avg_confidence = session.query(
            func.avg(cls.confidence_score)
        ).filter(
            cls.is_deleted == False,
            cls.confidence_score.isnot(None)
        ).scalar()
        
        return {
            "total_documents": total,
            "by_status": {status: count for status, count in by_status},
            "by_type": {doc_type: count for doc_type, count in by_type},
            "average_confidence": float(avg_confidence) if avg_confidence else 0.0,
        }
