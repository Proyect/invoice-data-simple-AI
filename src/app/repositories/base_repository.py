"""
Repository Base
===============

Repository base con operaciones CRUD comunes.
"""
import logging
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic, Union
from datetime import datetime

from sqlalchemy.orm import Session, Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_, func, desc, asc

from ..core.database import Base
from ..services.cache_optimized import cache_service, cached, cache_invalidate

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=Base)


class BaseRepository(Generic[T]):
    """Repository base con operaciones CRUD comunes"""
    
    def __init__(self, model: Type[T], db: Session):
        self.model = model
        self.db = db
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
    
    def create(self, **kwargs) -> T:
        """Crear nueva entidad"""
        try:
            entity = self.model(**kwargs)
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            
            self.logger.info(f"Created {self.model.__name__} with ID: {entity.id}")
            return entity
            
        except SQLAlchemyError as e:
            self.db.rollback()
            self.logger.error(f"Error creating {self.model.__name__}: {e}")
            raise
    
    def get_by_id(self, entity_id: int) -> Optional[T]:
        """Obtener entidad por ID"""
        try:
            return self.db.query(self.model).filter(
                self.model.id == entity_id,
                getattr(self.model, 'is_deleted', False) == False
            ).first()
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting {self.model.__name__} by ID {entity_id}: {e}")
            raise
    
    def get_by_uuid(self, uuid: str) -> Optional[T]:
        """Obtener entidad por UUID"""
        try:
            return self.db.query(self.model).filter(
                getattr(self.model, 'uuid', None) == uuid,
                getattr(self.model, 'is_deleted', False) == False
            ).first()
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting {self.model.__name__} by UUID {uuid}: {e}")
            raise
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Obtener todas las entidades con paginación"""
        try:
            query = self.db.query(self.model).filter(
                getattr(self.model, 'is_deleted', False) == False
            )
            
            return query.offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting all {self.model.__name__}: {e}")
            raise
    
    def update(self, entity_id: int, **kwargs) -> Optional[T]:
        """Actualizar entidad"""
        try:
            entity = self.get_by_id(entity_id)
            if not entity:
                return None
            
            for key, value in kwargs.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
            
            entity.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(entity)
            
            self.logger.info(f"Updated {self.model.__name__} with ID: {entity_id}")
            return entity
            
        except SQLAlchemyError as e:
            self.db.rollback()
            self.logger.error(f"Error updating {self.model.__name__} with ID {entity_id}: {e}")
            raise
    
    def delete(self, entity_id: int, soft: bool = True) -> bool:
        """Eliminar entidad (soft delete por defecto)"""
        try:
            entity = self.get_by_id(entity_id)
            if not entity:
                return False
            
            if soft and hasattr(entity, 'is_deleted'):
                # Soft delete
                entity.is_deleted = True
                entity.deleted_at = datetime.utcnow()
                self.db.commit()
                self.logger.info(f"Soft deleted {self.model.__name__} with ID: {entity_id}")
            else:
                # Hard delete
                self.db.delete(entity)
                self.db.commit()
                self.logger.info(f"Hard deleted {self.model.__name__} with ID: {entity_id}")
            
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            self.logger.error(f"Error deleting {self.model.__name__} with ID {entity_id}: {e}")
            raise
    
    def restore(self, entity_id: int) -> bool:
        """Restaurar entidad eliminada"""
        try:
            entity = self.db.query(self.model).filter(
                self.model.id == entity_id,
                getattr(self.model, 'is_deleted', False) == True
            ).first()
            
            if not entity:
                return False
            
            entity.is_deleted = False
            entity.deleted_at = None
            self.db.commit()
            
            self.logger.info(f"Restored {self.model.__name__} with ID: {entity_id}")
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            self.logger.error(f"Error restoring {self.model.__name__} with ID {entity_id}: {e}")
            raise
    
    def count(self, **filters) -> int:
        """Contar entidades con filtros"""
        try:
            query = self.db.query(self.model).filter(
                getattr(self.model, 'is_deleted', False) == False
            )
            
            # Aplicar filtros
            for key, value in filters.items():
                if hasattr(self.model, key):
                    if isinstance(value, list):
                        query = query.filter(getattr(self.model, key).in_(value))
                    else:
                        query = query.filter(getattr(self.model, key) == value)
            
            return query.count()
        except SQLAlchemyError as e:
            self.logger.error(f"Error counting {self.model.__name__}: {e}")
            raise
    
    def exists(self, entity_id: int) -> bool:
        """Verificar si existe entidad"""
        try:
            return self.db.query(self.model).filter(
                self.model.id == entity_id,
                getattr(self.model, 'is_deleted', False) == False
            ).exists()
        except SQLAlchemyError as e:
            self.logger.error(f"Error checking existence of {self.model.__name__} with ID {entity_id}: {e}")
            raise
    
    def search(self, query: str, fields: List[str], skip: int = 0, limit: int = 100) -> List[T]:
        """Búsqueda en campos específicos"""
        try:
            db_query = self.db.query(self.model).filter(
                getattr(self.model, 'is_deleted', False) == False
            )
            
            # Construir condiciones de búsqueda
            search_conditions = []
            for field in fields:
                if hasattr(self.model, field):
                    search_conditions.append(
                        getattr(self.model, field).ilike(f"%{query}%")
                    )
            
            if search_conditions:
                db_query = db_query.filter(or_(*search_conditions))
            
            return db_query.offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            self.logger.error(f"Error searching {self.model.__name__}: {e}")
            raise
    
    def filter_by(self, **filters) -> Query:
        """Filtrar entidades por criterios"""
        try:
            query = self.db.query(self.model).filter(
                getattr(self.model, 'is_deleted', False) == False
            )
            
            for key, value in filters.items():
                if hasattr(self.model, key):
                    if isinstance(value, list):
                        query = query.filter(getattr(self.model, key).in_(value))
                    elif isinstance(value, dict):
                        # Soporte para operadores
                        operator = value.get('operator', 'eq')
                        val = value.get('value')
                        
                        if operator == 'eq':
                            query = query.filter(getattr(self.model, key) == val)
                        elif operator == 'ne':
                            query = query.filter(getattr(self.model, key) != val)
                        elif operator == 'gt':
                            query = query.filter(getattr(self.model, key) > val)
                        elif operator == 'gte':
                            query = query.filter(getattr(self.model, key) >= val)
                        elif operator == 'lt':
                            query = query.filter(getattr(self.model, key) < val)
                        elif operator == 'lte':
                            query = query.filter(getattr(self.model, key) <= val)
                        elif operator == 'like':
                            query = query.filter(getattr(self.model, key).ilike(f"%{val}%"))
                        elif operator == 'in':
                            query = query.filter(getattr(self.model, key).in_(val))
                        elif operator == 'not_in':
                            query = query.filter(~getattr(self.model, key).in_(val))
                    else:
                        query = query.filter(getattr(self.model, key) == value)
            
            return query
        except SQLAlchemyError as e:
            self.logger.error(f"Error filtering {self.model.__name__}: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de la entidad"""
        try:
            total = self.count()
            
            # Estadísticas por fecha de creación
            monthly_stats = self.db.query(
                func.date_trunc('month', self.model.created_at).label('month'),
                func.count(self.model.id).label('count')
            ).filter(
                getattr(self.model, 'is_deleted', False) == False
            ).group_by('month').order_by('month').all()
            
            return {
                'total': total,
                'monthly': [
                    {'month': month.strftime('%Y-%m'), 'count': count}
                    for month, count in monthly_stats
                ]
            }
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting stats for {self.model.__name__}: {e}")
            raise
    
    def bulk_create(self, entities_data: List[Dict[str, Any]]) -> List[T]:
        """Crear múltiples entidades en lote"""
        try:
            entities = []
            for data in entities_data:
                entity = self.model(**data)
                entities.append(entity)
                self.db.add(entity)
            
            self.db.commit()
            
            for entity in entities:
                self.db.refresh(entity)
            
            self.logger.info(f"Bulk created {len(entities)} {self.model.__name__} entities")
            return entities
            
        except SQLAlchemyError as e:
            self.db.rollback()
            self.logger.error(f"Error bulk creating {self.model.__name__}: {e}")
            raise
    
    def bulk_update(self, updates: List[Dict[str, Any]]) -> int:
        """Actualizar múltiples entidades en lote"""
        try:
            updated_count = 0
            
            for update_data in updates:
                entity_id = update_data.pop('id')
                entity = self.get_by_id(entity_id)
                
                if entity:
                    for key, value in update_data.items():
                        if hasattr(entity, key):
                            setattr(entity, key, value)
                    updated_count += 1
            
            self.db.commit()
            self.logger.info(f"Bulk updated {updated_count} {self.model.__name__} entities")
            return updated_count
            
        except SQLAlchemyError as e:
            self.db.rollback()
            self.logger.error(f"Error bulk updating {self.model.__name__}: {e}")
            raise
    
    def bulk_delete(self, entity_ids: List[int], soft: bool = True) -> int:
        """Eliminar múltiples entidades en lote"""
        try:
            deleted_count = 0
            
            for entity_id in entity_ids:
                if self.delete(entity_id, soft=soft):
                    deleted_count += 1
            
            self.logger.info(f"Bulk deleted {deleted_count} {self.model.__name__} entities")
            return deleted_count
            
        except SQLAlchemyError as e:
            self.logger.error(f"Error bulk deleting {self.model.__name__}: {e}")
            raise
