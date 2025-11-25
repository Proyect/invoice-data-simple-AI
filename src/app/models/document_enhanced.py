"""
Modelo de Documento Mejorado con relaciones y funcionalidades avanzadas
"""
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, Float, 
    ForeignKey, Index, func, JSON, Enum as SQLEnum, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR, UUID
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.hybrid import hybrid_property
from ..core.database import Base
from ..core.config import settings
import enum
from datetime import datetime
from typing import Dict, Any, Optional, List
import uuid


class DocumentType(enum.Enum):
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


class DocumentStatus(enum.Enum):
    """Estados del procesamiento del documento"""
    UPLOADED = "uploaded"           # Subido, pendiente de procesar
    PROCESSING = "processing"       # En procesamiento
    PROCESSED = "processed"         # Procesado exitosamente
    FAILED = "failed"              # Error en procesamiento
    REVIEWING = "reviewing"         # En revisión manual
    APPROVED = "approved"          # Aprobado
    REJECTED = "rejected"          # Rechazado


class OCRProvider(enum.Enum):
    """Proveedores de OCR disponibles"""
    TESSERACT = "tesseract"
    GOOGLE_VISION = "google_vision"
    AWS_TEXTRACT = "aws_textract"
    AZURE_OCR = "azure_ocr"
    HYBRID = "hybrid"


class ExtractionMethod(enum.Enum):
    """Métodos de extracción de datos"""
    REGEX = "regex"
    SPACY = "spacy"
    LLM = "llm"
    HYBRID = "hybrid"
    MANUAL = "manual"


class Document(Base):
    """Modelo de Documento con funcionalidades avanzadas"""
    __tablename__ = "documents"

    # Identificadores
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), index=True)
    
    # Información del archivo
    filename = Column(String(255), nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)
    file_hash = Column(String(64), nullable=True, index=True)  # SHA-256 para detectar duplicados
    
    # Clasificación y estado
    document_type = Column(SQLEnum(DocumentType), nullable=True, index=True)
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.UPLOADED, index=True)
    priority = Column(Integer, default=5, nullable=False)  # 1=alta, 5=normal, 10=baja
    
    # Datos extraídos
    raw_text = Column(Text, nullable=True)
    extracted_data = Column(JSON, nullable=True)  # Datos estructurados
    confidence_score = Column(Float, nullable=True)  # 0.0 - 1.0
    quality_score = Column(Float, nullable=True)    # Calidad del documento original
    
    # Metadatos de procesamiento
    ocr_provider = Column(SQLEnum(OCRProvider), nullable=True)
    extraction_method = Column(SQLEnum(ExtractionMethod), nullable=True)
    ocr_cost = Column(Float, default=0.0)
    processing_time_seconds = Column(Float, nullable=True)
    
    # Metadatos adicionales
    language = Column(String(10), default='es', nullable=False)
    page_count = Column(Integer, nullable=True)
    word_count = Column(Integer, nullable=True)
    
    # Relaciones
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=True, index=True)
    
    # Auditoría y timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Campos para revisión manual
    reviewed_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    review_notes = Column(Text, nullable=True)
    
    # Búsqueda full-text (PostgreSQL)
    search_vector = Column(TSVECTOR, nullable=True)
    
    # Soft delete
    is_deleted = Column(Boolean, default=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relaciones ORM
    user = relationship("User", foreign_keys=[user_id], back_populates="documents")
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    organization = relationship("Organization", back_populates="documents")
    extractions = relationship("DocumentExtraction", back_populates="document", cascade="all, delete-orphan")
    versions = relationship("DocumentVersion", back_populates="document", cascade="all, delete-orphan")
    tags = relationship("DocumentTag", back_populates="document", cascade="all, delete-orphan")
    
    # Índices compuestos optimizados para consultas comunes
    __table_args__ = (
        # Índices para filtrado por usuario/organización
        Index('ix_documents_user_status', 'user_id', 'status'),
        Index('ix_documents_org_status', 'organization_id', 'status'),
        Index('ix_documents_user_org', 'user_id', 'organization_id'),
        
        # Índices para filtrado por tipo y fecha
        Index('ix_documents_type_created', 'document_type', 'created_at'),
        Index('ix_documents_type_status', 'document_type', 'status'),
        
        # Índices para calidad y procesamiento
        Index('ix_documents_confidence_status', 'confidence_score', 'status'),
        Index('ix_documents_status_created', 'status', 'created_at'),
        Index('ix_documents_priority_status', 'priority', 'status'),
        
        # Índices para detección de duplicados
        Index('ix_documents_hash_size', 'file_hash', 'file_size'),
        UniqueConstraint('file_hash', 'file_size', name='uq_document_hash_size'),
        
        # Índices para soft delete
        Index('ix_documents_deleted_created', 'is_deleted', 'created_at'),
        Index('ix_documents_status_deleted', 'status', 'is_deleted'),
        
        # Índices para revisión
        Index('ix_documents_reviewed_by_status', 'reviewed_by', 'status'),
        Index('ix_documents_reviewed_at', 'reviewed_at'),
        
        # Índice para búsqueda por mime_type
        Index('ix_documents_mime_type', 'mime_type'),
    )
    
    @validates('confidence_score', 'quality_score')
    def validate_scores(self, key, value):
        """Validar que los scores estén entre 0 y 1"""
        if value is not None:
            if not isinstance(value, (int, float)):
                raise ValueError(f"{key} debe ser un número")
            if value < 0 or value > 1:
                raise ValueError(f"{key} debe estar entre 0 y 1")
        return value
    
    @validates('priority')
    def validate_priority(self, key, value):
        """Validar que la prioridad esté entre 1 y 10"""
        if not isinstance(value, int):
            raise ValueError("Priority debe ser un entero")
        if value < 1 or value > 10:
            raise ValueError("Priority debe estar entre 1 y 10")
        return value
    
    @validates('file_size')
    def validate_file_size(self, key, value):
        """Validar tamaño de archivo"""
        if value is not None:
            if not isinstance(value, int):
                raise ValueError("file_size debe ser un entero")
            if value < 0:
                raise ValueError("file_size no puede ser negativo")
            # Límite razonable: 500MB
            if value > 500 * 1024 * 1024:
                raise ValueError("file_size excede el límite máximo de 500MB")
        return value
    
    @validates('filename', 'original_filename')
    def validate_filename(self, key, value):
        """Validar nombre de archivo"""
        if not value or not isinstance(value, str):
            raise ValueError(f"{key} no puede estar vacío")
        if len(value) > 255:
            raise ValueError(f"{key} excede la longitud máxima de 255 caracteres")
        # Validar caracteres peligrosos
        dangerous_chars = ['..', '/', '\\', '\x00']
        for char in dangerous_chars:
            if char in value:
                raise ValueError(f"{key} contiene caracteres no permitidos")
        return value
    
    @validates('language')
    def validate_language(self, key, value):
        """Validar código de idioma"""
        if not value:
            return 'es'  # Default
        if not isinstance(value, str) or len(value) != 2:
            raise ValueError("language debe ser un código de 2 caracteres (ISO 639-1)")
        return value.lower()
    
    @hybrid_property
    def is_processed(self):
        """Indica si el documento ya fue procesado"""
        return self.status in [DocumentStatus.PROCESSED, DocumentStatus.APPROVED]
    
    @hybrid_property
    def needs_review(self):
        """Indica si el documento necesita revisión manual"""
        return (self.status == DocumentStatus.PROCESSED and 
                self.confidence_score is not None and 
                self.confidence_score < 0.8)
    
    @hybrid_property
    def file_size_mb(self):
        """Tamaño del archivo en MB"""
        return self.file_size / (1024 * 1024) if self.file_size else 0
    
    @hybrid_property
    def file_size_kb(self):
        """Tamaño del archivo en KB"""
        return self.file_size / 1024 if self.file_size else 0
    
    @hybrid_property
    def is_high_quality(self):
        """Indica si el documento es de alta calidad"""
        return (self.quality_score is not None and 
                self.quality_score >= 0.8 and 
                self.confidence_score is not None and 
                self.confidence_score >= 0.8)
    
    @hybrid_property
    def is_low_confidence(self):
        """Indica si el documento tiene baja confianza"""
        return (self.confidence_score is not None and 
                self.confidence_score < 0.6)
    
    @hybrid_property
    def processing_efficiency(self):
        """Eficiencia de procesamiento (páginas por segundo)"""
        if self.processing_time_seconds and self.page_count:
            return self.page_count / self.processing_time_seconds
        return None
    
    @hybrid_property
    def age_days(self):
        """Edad del documento en días"""
        if self.created_at:
            return (datetime.utcnow() - self.created_at).days
        return None
    
    @hybrid_property
    def processing_age_hours(self):
        """Tiempo desde el procesamiento en horas"""
        if self.processed_at:
            return (datetime.utcnow() - self.processed_at).total_seconds() / 3600
        return None
    
    def to_dict(self, include_extracted_data=True) -> Dict[str, Any]:
        """Convierte el documento a diccionario"""
        data = {
            "id": self.id,
            "uuid": self.uuid,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "file_size": self.file_size,
            "file_size_mb": self.file_size_mb,
            "mime_type": self.mime_type,
            "document_type": self.document_type.value if self.document_type else None,
            "status": self.status.value,
            "priority": self.priority,
            "confidence_score": self.confidence_score,
            "quality_score": self.quality_score,
            "ocr_provider": self.ocr_provider.value if self.ocr_provider else None,
            "extraction_method": self.extraction_method.value if self.extraction_method else None,
            "processing_time_seconds": self.processing_time_seconds,
            "language": self.language,
            "page_count": self.page_count,
            "word_count": self.word_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
            "is_processed": self.is_processed,
            "needs_review": self.needs_review,
        }
        
        if include_extracted_data:
            data["extracted_data"] = self.extracted_data
            data["raw_text"] = self.raw_text
        
        return data
    
    def update_search_vector(self, session):
        """Actualiza el vector de búsqueda full-text"""
        if "postgresql" in str(session.bind.url).lower() and self.raw_text:
            # Combinar texto y datos extraídos para búsqueda
            search_text = self.raw_text
            
            if self.extracted_data:
                # Agregar datos extraídos al texto de búsqueda
                def extract_text_from_dict(d, prefix=""):
                    texts = []
                    if isinstance(d, dict):
                        for key, value in d.items():
                            if isinstance(value, str):
                                texts.append(value)
                            elif isinstance(value, (dict, list)):
                                texts.extend(extract_text_from_dict(value, f"{prefix}{key}_"))
                    elif isinstance(d, list):
                        for item in d:
                            if isinstance(item, str):
                                texts.append(item)
                            elif isinstance(item, (dict, list)):
                                texts.extend(extract_text_from_dict(item, prefix))
                    return texts
                
                extracted_texts = extract_text_from_dict(self.extracted_data)
                search_text += " " + " ".join(extracted_texts)
            
            # Actualizar vector de búsqueda
            from sqlalchemy import text
            session.execute(
                text("UPDATE documents SET search_vector = to_tsvector('spanish', :search_text) WHERE id = :doc_id"),
                {"search_text": search_text, "doc_id": self.id}
            )
    
    def mark_as_processed(self, confidence_score: float = None, processing_time: float = None):
        """Marca el documento como procesado"""
        self.status = DocumentStatus.PROCESSED
        self.processed_at = datetime.utcnow()
        if confidence_score is not None:
            self.confidence_score = confidence_score
        if processing_time is not None:
            self.processing_time_seconds = processing_time
    
    def mark_as_failed(self, error_message: str = None):
        """Marca el documento como fallido"""
        self.status = DocumentStatus.FAILED
        if error_message:
            self.review_notes = error_message
    
    def soft_delete(self):
        """Eliminación lógica del documento"""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
    
    def restore(self):
        """Restaura un documento eliminado lógicamente"""
        self.is_deleted = False
        self.deleted_at = None
    
    def approve(self, reviewer_id: int, notes: str = None):
        """Aprueba el documento"""
        self.status = DocumentStatus.APPROVED
        self.reviewed_by = reviewer_id
        self.reviewed_at = datetime.utcnow()
        if notes:
            self.review_notes = notes
    
    def reject(self, reviewer_id: int, reason: str):
        """Rechaza el documento"""
        self.status = DocumentStatus.REJECTED
        self.reviewed_by = reviewer_id
        self.reviewed_at = datetime.utcnow()
        self.review_notes = reason
    
    def request_review(self, reason: str = None):
        """Solicita revisión manual del documento"""
        self.status = DocumentStatus.REVIEWING
        if reason:
            self.review_notes = reason
    
    def update_extracted_data(self, data: Dict[str, Any], confidence: float = None):
        """Actualiza los datos extraídos y confianza"""
        self.extracted_data = data
        if confidence is not None:
            self.confidence_score = confidence
        self.updated_at = datetime.utcnow()
    
    def add_tag(self, tag_name: str, tag_value: str = None, user_id: int = None):
        """Agrega un tag al documento (requiere sesión de DB)"""
        # Nota: Este método requiere acceso a la sesión de DB
        # Se implementaría en el repositorio o servicio
        pass
    
    def get_extraction_summary(self) -> Dict[str, Any]:
        """Obtiene un resumen de las extracciones"""
        if not self.extracted_data:
            return {}
        
        summary = {
            "total_fields": len(self.extracted_data),
            "fields_with_values": sum(1 for v in self.extracted_data.values() if v),
            "extraction_method": self.extraction_method.value if self.extraction_method else None,
            "ocr_provider": self.ocr_provider.value if self.ocr_provider else None,
            "confidence": self.confidence_score,
        }
        
        return summary
    
    def can_be_reprocessed(self) -> bool:
        """Indica si el documento puede ser reprocesado"""
        return self.status in [
            DocumentStatus.FAILED,
            DocumentStatus.REJECTED,
            DocumentStatus.PROCESSED
        ]
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.filename}', status='{self.status.value}')>"


class DocumentVersion(Base):
    """Versiones de documentos para auditoría"""
    __tablename__ = "document_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    
    # Snapshot de datos en esta versión
    extracted_data_snapshot = Column(JSON, nullable=True)
    confidence_score_snapshot = Column(Float, nullable=True)
    ocr_provider_snapshot = Column(String(50), nullable=True)
    
    # Metadatos de la versión
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    change_reason = Column(String(255), nullable=True)
    
    # Relaciones
    document = relationship("Document", back_populates="versions")
    creator = relationship("User")
    
    __table_args__ = (
        UniqueConstraint('document_id', 'version_number', name='uq_document_version'),
        Index('ix_document_versions_created', 'created_at'),
    )


class DocumentExtraction(Base):
    """Múltiples extracciones por documento (diferentes métodos)"""
    __tablename__ = "document_extractions"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=False, index=True)
    
    # Método de extracción
    extraction_method = Column(SQLEnum(ExtractionMethod), nullable=False)
    ocr_provider = Column(SQLEnum(OCRProvider), nullable=True)
    
    # Resultados
    extracted_data = Column(JSON, nullable=True)
    confidence_score = Column(Float, nullable=True)
    processing_time_seconds = Column(Float, nullable=True)
    cost = Column(Float, default=0.0)
    
    # Metadatos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Relaciones
    document = relationship("Document", back_populates="extractions")
    creator = relationship("User")
    
    __table_args__ = (
        Index('ix_extractions_method_confidence', 'extraction_method', 'confidence_score'),
    )


class DocumentTag(Base):
    """Tags/etiquetas para documentos"""
    __tablename__ = "document_tags"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=False, index=True)
    tag_name = Column(String(100), nullable=False, index=True)
    tag_value = Column(String(255), nullable=True)
    
    # Metadatos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Relaciones
    document = relationship("Document", back_populates="tags")
    creator = relationship("User")
    
    __table_args__ = (
        UniqueConstraint('document_id', 'tag_name', name='uq_document_tag'),
        Index('ix_tags_name_value', 'tag_name', 'tag_value'),
    )


class Organization(Base):
    """Organizaciones para multi-tenancy"""
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Configuración
    settings = Column(JSON, nullable=True)  # Configuraciones específicas de la org
    is_active = Column(Boolean, default=True, index=True)
    
    # Límites y cuotas
    document_limit = Column(Integer, nullable=True)  # Límite de documentos
    storage_limit_mb = Column(Integer, nullable=True)  # Límite de almacenamiento
    
    # Estadísticas (pre-calculadas para optimización)
    total_documents = Column(Integer, default=0, nullable=False)
    total_storage_mb = Column(Float, default=0.0, nullable=False)
    active_users_count = Column(Integer, default=0, nullable=False)
    
    # Metadatos adicionales
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(20), nullable=True)
    website = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relaciones con lazy loading optimizado
    documents = relationship(
        "Document", 
        back_populates="organization",
        lazy="dynamic",  # Para evitar cargar todos los documentos
        cascade="all, delete-orphan"
    )
    users = relationship(
        "User", 
        back_populates="organization",
        lazy="dynamic",
        cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        Index('ix_organizations_active_created', 'is_active', 'created_at'),
    )
    
    @validates('slug')
    def validate_slug(self, key, value):
        """Validar formato de slug"""
        import re
        if not re.match(r'^[a-z0-9-]+$', value):
            raise ValueError("slug solo puede contener letras minúsculas, números y guiones")
        if len(value) < 3 or len(value) > 100:
            raise ValueError("slug debe tener entre 3 y 100 caracteres")
        return value.lower()
    
    @validates('name')
    def validate_name(self, key, value):
        """Validar nombre de organización"""
        if not value or len(value.strip()) == 0:
            raise ValueError("name no puede estar vacío")
        if len(value) > 255:
            raise ValueError("name excede la longitud máxima")
        return value.strip()
    
    @hybrid_property
    def storage_usage_percentage(self):
        """Porcentaje de almacenamiento usado"""
        if not self.storage_limit_mb:
            return None
        return (self.total_storage_mb / self.storage_limit_mb) * 100 if self.storage_limit_mb > 0 else 0
    
    @hybrid_property
    def document_usage_percentage(self):
        """Porcentaje de documentos usados"""
        if not self.document_limit:
            return None
        return (self.total_documents / self.document_limit) * 100 if self.document_limit > 0 else 0
    
    @hybrid_property
    def is_over_limit(self):
        """Indica si la organización excede sus límites"""
        storage_over = (self.storage_limit_mb and 
                       self.total_storage_mb > self.storage_limit_mb)
        docs_over = (self.document_limit and 
                     self.total_documents > self.document_limit)
        return storage_over or docs_over
    
    def increment_document_count(self, file_size_mb: float = 0):
        """Incrementa contadores de documentos y almacenamiento"""
        self.total_documents += 1
        if file_size_mb:
            self.total_storage_mb += file_size_mb
    
    def decrement_document_count(self, file_size_mb: float = 0):
        """Decrementa contadores de documentos y almacenamiento"""
        self.total_documents = max(0, self.total_documents - 1)
        if file_size_mb:
            self.total_storage_mb = max(0.0, self.total_storage_mb - file_size_mb)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la organización a diccionario"""
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "is_active": self.is_active,
            "total_documents": self.total_documents,
            "total_storage_mb": self.total_storage_mb,
            "active_users_count": self.active_users_count,
            "document_limit": self.document_limit,
            "storage_limit_mb": self.storage_limit_mb,
            "storage_usage_percentage": self.storage_usage_percentage,
            "document_usage_percentage": self.document_usage_percentage,
            "is_over_limit": self.is_over_limit,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self):
        return f"<Organization(id={self.id}, name='{self.name}')>"

















