"""
Modelos Base
============

Modelos base con funcionalidades comunes para todos los modelos del sistema.
"""
import uuid
from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from ..core.database import Base


class BaseModel(Base):
    """Modelo base con campos comunes"""
    __abstract__ = True
    
    # Campos comunes
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadatos
    metadata_json = Column(Text, nullable=True)  # JSON como texto para compatibilidad
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id}, uuid='{self.uuid}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir modelo a diccionario"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def soft_delete(self, session: Session) -> None:
        """Eliminación lógica"""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        session.commit()
    
    def restore(self, session: Session) -> None:
        """Restaurar después de eliminación lógica"""
        self.is_deleted = False
        self.deleted_at = None
        session.commit()
    
    @classmethod
    def get_by_uuid(cls, session: Session, uuid: str) -> Optional['BaseModel']:
        """Obtener por UUID"""
        return session.query(cls).filter(
            cls.uuid == uuid,
            cls.is_deleted == False
        ).first()
    
    @classmethod
    def get_active(cls, session: Session) -> 'Query':
        """Obtener solo registros activos"""
        return session.query(cls).filter(cls.is_deleted == False)


class TimestampMixin:
    """Mixin para agregar timestamps a cualquier modelo"""
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class SoftDeleteMixin:
    """Mixin para eliminación lógica"""
    
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    def soft_delete(self, session: Session) -> None:
        """Eliminación lógica"""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        session.commit()
    
    def restore(self, session: Session) -> None:
        """Restaurar después de eliminación lógica"""
        self.is_deleted = False
        self.deleted_at = None
        session.commit()


class MetadataMixin:
    """Mixin para metadatos JSON"""
    
    metadata_json = Column(Text, nullable=True)
    
    def get_metadata(self) -> Dict[str, Any]:
        """Obtener metadatos como diccionario"""
        if self.metadata_json:
            import json
            return json.loads(self.metadata_json)
        return {}
    
    def set_metadata(self, metadata: Dict[str, Any]) -> None:
        """Establecer metadatos"""
        import json
        self.metadata_json = json.dumps(metadata)
    
    def update_metadata(self, **kwargs) -> None:
        """Actualizar metadatos"""
        current = self.get_metadata()
        current.update(kwargs)
        self.set_metadata(current)


class SearchableMixin:
    """Mixin para búsqueda full-text"""
    
    @declared_attr
    def search_vector(cls):
        """Vector de búsqueda (solo PostgreSQL)"""
        # Solo se crea si es PostgreSQL
        from ..core.database import engine
        if engine and "postgresql" in str(engine.url):
            from sqlalchemy.dialects.postgresql import TSVECTOR
            return Column(TSVECTOR, nullable=True)
        return None
    
    def update_search_vector(self) -> None:
        """Actualizar vector de búsqueda"""
        if hasattr(self, 'search_vector') and self.search_vector is not None:
            # Implementar lógica de actualización de vector de búsqueda
            pass
