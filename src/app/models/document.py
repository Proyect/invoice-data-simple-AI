from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Index, func, JSON, Float, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from ..core.database import Base


class DocumentStatusValues:
    """Valores de estado del documento (string). Evita duplicar enums con models_v2."""
    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    REVIEWING = "reviewing"
    APPROVED = "approved"
    REJECTED = "rejected"


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)
    
    # Columnas requeridas por la base de datos (NOT NULL)
    status = Column(String(50), nullable=False, default="pending", server_default="pending")
    priority = Column(Integer, nullable=False, default=5, server_default="5")
    language = Column(String(10), nullable=False, default="es", server_default="es")
    is_deleted = Column(Boolean, nullable=False, default=False, server_default="false")
    
    # Datos extraídos - JSON para SQLite, JSONB para PostgreSQL
    raw_text = Column(Text, nullable=True)
    # Usar JSONB para PostgreSQL (avanzado), JSON para SQLite
    extracted_data = Column(JSON, nullable=True)
    confidence_score = Column(Float, nullable=True)  # 0.0–1.0
    
    # Metadatos de procesamiento
    ocr_provider = Column(String(50), nullable=True)
    ocr_cost = Column(Float, nullable=True)
    processing_time = Column(String(20), nullable=True)
    processing_time_seconds = Column(Float, nullable=True)
    document_type = Column(String(50), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    organization_id = Column(Integer, nullable=True, index=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    review_notes = Column(Text, nullable=True)
    reviewed_by = Column(Integer, nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    tag_list = Column(JSON, nullable=True)  # lista de strings (evitar nombre 'tags' por conflicto con document_enhanced)

    # Búsqueda full-text (solo PostgreSQL, SQLite no soporta TSVECTOR)
    # Temporalmente comentado para compatibilidad con tests SQLite
    # if "postgresql" in settings.DATABASE_URL.lower():
    #     search_vector = Column(TSVECTOR, nullable=True)
    
    # Metadatos
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Índices básicos para SQLite; extend_existing para tests que recargan el modelo
    __table_args__ = (
        Index('ix_documents_filename_created', 'filename', 'created_at'),
        Index('ix_documents_confidence', 'confidence_score'),
        Index('ix_documents_mime_type', 'mime_type'),
        Index('ix_documents_ocr_provider', 'ocr_provider'),
        {"extend_existing": True},
    )
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.filename}')>"

    @property
    def file_size_mb(self):
        """Tamaño del archivo en MB."""
        return round(self.file_size / (1024 * 1024), 2) if self.file_size else 0.0

    @property
    def is_processed(self):
        """Indica si el documento está procesado o aprobado."""
        return str(self.status or "") in (DocumentStatusValues.PROCESSED, DocumentStatusValues.APPROVED)

    @property
    def needs_review(self):
        """Indica si necesita revisión (procesado con confianza baja)."""
        return (
            str(self.status or "") == DocumentStatusValues.PROCESSED
            and self.confidence_score is not None
            and self.confidence_score < 0.8
        )

    def set_extracted_data(self, data):
        """Asigna datos extraídos (dict/JSON)."""
        self.extracted_data = data

    def get_extracted_data(self):
        """Devuelve datos extraídos como dict."""
        return self.extracted_data if self.extracted_data else {}

    def get_tags(self):
        """Devuelve la lista de tags."""
        return list(self.tag_list) if self.tag_list else []

    def set_tags(self, tags_list):
        """Asigna la lista de tags."""
        self.tag_list = list(tags_list) if tags_list else []

    def add_tag(self, tag: str):
        """Añade un tag si no existe."""
        current = self.get_tags()
        if tag not in current:
            current.append(tag)
            self.tag_list = current

    def remove_tag(self, tag: str):
        """Elimina un tag."""
        current = self.get_tags()
        if tag in current:
            current.remove(tag)
            self.tag_list = current

    def mark_processing(self, session):
        """Marca el documento como en procesamiento."""
        self.status = DocumentStatusValues.PROCESSING
        session.commit()
        session.refresh(self)

    def mark_processed(self, session, confidence_score: float = None, processing_time: float = None):
        """Marca el documento como procesado."""
        self.status = DocumentStatusValues.PROCESSED
        self.processed_at = datetime.utcnow()
        if confidence_score is not None:
            self.confidence_score = float(confidence_score)
        if processing_time is not None:
            self.processing_time_seconds = float(processing_time)
        session.commit()
        session.refresh(self)

    def mark_failed(self, session, error_message: str = None):
        """Marca el documento como fallido."""
        self.status = DocumentStatusValues.FAILED
        if error_message:
            self.review_notes = error_message
        session.commit()
        session.refresh(self)

    def update_search_vector(self):
        """Actualiza el vector de búsqueda full-text (solo PostgreSQL)"""
        # Temporalmente comentado para compatibilidad con tests SQLite
        # if "postgresql" in settings.DATABASE_URL.lower() and self.raw_text:
        #     # Crear vector de búsqueda combinando texto y datos extraídos
        #     search_text = self.raw_text
        #     if self.extracted_data:
        #         # Agregar datos extraídos al texto de búsqueda
        #         for key, value in self.extracted_data.items():
        #             if isinstance(value, str):
        #                 search_text += f" {value}"
        #             elif isinstance(value, list):
        #                 search_text += f" {' '.join(str(v) for v in value)}"
        #     
        #     # Crear TSVECTOR (se hace en la base de datos)
        #     self.search_vector = func.to_tsvector('spanish', search_text)
        pass
