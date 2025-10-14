from sqlalchemy import Column, Integer, String, Text, DateTime, Index, func, JSON
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from app.core.database import Base
from app.core.config import settings

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)
    
    # Datos extraídos - JSON para SQLite, JSONB para PostgreSQL
    raw_text = Column(Text, nullable=True)
    # Usar JSONB para PostgreSQL (avanzado), JSON para SQLite
    extracted_data = Column(JSON, nullable=True)
    confidence_score = Column(Integer, nullable=True)
    
    # Metadatos de procesamiento
    ocr_provider = Column(String(50), nullable=True)
    ocr_cost = Column(String(20), nullable=True)
    processing_time = Column(String(20), nullable=True)
    
    # Búsqueda full-text (solo PostgreSQL, SQLite no soporta TSVECTOR)
    # Temporalmente comentado para compatibilidad con tests SQLite
    # if "postgresql" in settings.DATABASE_URL.lower():
    #     search_vector = Column(TSVECTOR, nullable=True)
    
    # Metadatos
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Índices básicos para SQLite (temporalmente simplificado para tests)
    __table_args__ = (
        Index('ix_documents_filename_created', 'filename', 'created_at'),
        Index('ix_documents_confidence', 'confidence_score'),
        Index('ix_documents_mime_type', 'mime_type'),
        Index('ix_documents_ocr_provider', 'ocr_provider'),
    )
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.filename}')>"
    
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
