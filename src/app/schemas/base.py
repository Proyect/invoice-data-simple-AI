"""
Schemas Base
============

Schemas base con funcionalidades comunes para todos los schemas del sistema.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List, Union
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic.types import conint, confloat


class BaseSchema(BaseModel):
    """Schema base con configuración común"""
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            UUID: lambda v: str(v) if v else None,
        }
        validate_assignment = True
        use_enum_values = True


class TimestampSchema(BaseSchema):
    """Schema con timestamps"""
    created_at: datetime = Field(description="Fecha de creación")
    updated_at: datetime = Field(description="Fecha de última actualización")


class SoftDeleteSchema(BaseSchema):
    """Schema con campos de eliminación lógica"""
    is_deleted: bool = Field(default=False, description="Indica si está eliminado")
    deleted_at: Optional[datetime] = Field(None, description="Fecha de eliminación")


class MetadataSchema(BaseSchema):
    """Schema con metadatos"""
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadatos adicionales")


class PaginationSchema(BaseSchema):
    """Schema para paginación"""
    page: conint(ge=1) = Field(1, description="Página actual")
    size: conint(ge=1, le=100) = Field(20, description="Tamaño de página")
    total: conint(ge=0) = Field(0, description="Total de elementos")
    total_pages: conint(ge=0) = Field(0, description="Total de páginas")
    has_next: bool = Field(False, description="Tiene página siguiente")
    has_prev: bool = Field(False, description="Tiene página anterior")
    
    @model_validator(mode='after')
    def calculate_pagination(self):
        """Calcular campos de paginación"""
        if self.total > 0:
            self.total_pages = (self.total + self.size - 1) // self.size
            self.has_next = self.page < self.total_pages
            self.has_prev = self.page > 1
        return self


class SearchSchema(BaseSchema):
    """Schema para búsqueda"""
    query: Optional[str] = Field(None, max_length=500, description="Consulta de búsqueda")
    filters: Optional[Dict[str, Any]] = Field(None, description="Filtros adicionales")
    sort_by: str = Field("created_at", description="Campo de ordenamiento")
    sort_order: str = Field("desc", description="Orden de clasificación")
    
    @field_validator('sort_order')
    @classmethod
    def validate_sort_order(cls, v):
        if v not in ['asc', 'desc']:
            raise ValueError('sort_order must be "asc" or "desc"')
        return v


class ResponseSchema(BaseSchema):
    """Schema base para respuestas"""
    success: bool = Field(True, description="Indica si la operación fue exitosa")
    message: Optional[str] = Field(None, description="Mensaje de respuesta")
    data: Optional[Any] = Field(None, description="Datos de respuesta")


class ErrorSchema(BaseSchema):
    """Schema para errores"""
    error: str = Field(..., description="Tipo de error")
    code: int = Field(..., description="Código de error")
    message: str = Field(..., description="Mensaje de error")
    details: Optional[Dict[str, Any]] = Field(None, description="Detalles del error")


class ValidationErrorSchema(ErrorSchema):
    """Schema para errores de validación"""
    error: str = Field("ValidationError", description="Tipo de error")
    code: int = Field(422, description="Código de error")
    field_errors: List[Dict[str, Any]] = Field(..., description="Errores por campo")


class FileSchema(BaseSchema):
    """Schema para archivos"""
    filename: str = Field(..., min_length=1, max_length=255, description="Nombre del archivo")
    original_filename: str = Field(..., min_length=1, max_length=255, description="Nombre original")
    file_size: Optional[conint(ge=0)] = Field(None, description="Tamaño en bytes")
    mime_type: Optional[str] = Field(None, max_length=100, description="Tipo MIME")
    
    @field_validator('filename', 'original_filename')
    @classmethod
    def validate_filename(cls, v):
        """Validar nombre de archivo"""
        if not v or v.strip() == "":
            raise ValueError("El nombre del archivo no puede estar vacío")
        
        # Caracteres peligrosos
        dangerous_chars = ['..', '/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in dangerous_chars:
            if char in v:
                raise ValueError(f"El nombre del archivo no puede contener '{char}'")
        
        return v.strip()


class ConfidenceSchema(BaseSchema):
    """Schema para puntuaciones de confianza"""
    confidence_score: Optional[confloat(ge=0.0, le=1.0)] = Field(None, description="Puntuación de confianza (0.0-1.0)")
    quality_score: Optional[confloat(ge=0.0, le=1.0)] = Field(None, description="Puntuación de calidad (0.0-1.0)")


class ProcessingSchema(BaseSchema):
    """Schema para información de procesamiento"""
    processing_time_seconds: Optional[confloat(ge=0.0)] = Field(None, description="Tiempo de procesamiento en segundos")
    ocr_cost: Optional[confloat(ge=0.0)] = Field(None, description="Costo de OCR")
    page_count: Optional[conint(ge=0)] = Field(None, description="Número de páginas")
    word_count: Optional[conint(ge=0)] = Field(None, description="Número de palabras")


class TagsSchema(BaseSchema):
    """Schema para tags"""
    tags: List[str] = Field(default_factory=list, description="Lista de tags")
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        """Validar tags"""
        if len(v) > 20:
            raise ValueError("No se pueden tener más de 20 tags")
        
        for tag in v:
            if not tag or len(tag.strip()) == 0:
                raise ValueError("Los tags no pueden estar vacíos")
            if len(tag) > 100:
                raise ValueError("Cada tag no puede tener más de 100 caracteres")
        
        return [tag.strip().lower() for tag in v]


class StatsSchema(BaseSchema):
    """Schema para estadísticas"""
    total: conint(ge=0) = Field(..., description="Total de elementos")
    by_category: Dict[str, int] = Field(default_factory=dict, description="Conteo por categoría")
    average_value: Optional[confloat(ge=0.0)] = Field(None, description="Valor promedio")
    min_value: Optional[confloat(ge=0.0)] = Field(None, description="Valor mínimo")
    max_value: Optional[confloat(ge=0.0)] = Field(None, description="Valor máximo")


class BatchOperationSchema(BaseSchema):
    """Schema para operaciones en lote"""
    operation: str = Field(..., description="Tipo de operación")
    item_ids: List[conint(ge=1)] = Field(..., min_items=1, max_items=100, description="IDs de elementos")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Parámetros de la operación")
    
    @field_validator('operation')
    @classmethod
    def validate_operation(cls, v):
        """Validar tipo de operación"""
        valid_operations = [
            'delete', 'update_status', 'update_type', 
            'add_tags', 'remove_tags', 'approve', 'reject'
        ]
        if v not in valid_operations:
            raise ValueError(f"Operación no válida. Debe ser una de: {valid_operations}")
        return v


class ExportSchema(BaseSchema):
    """Schema para exportación"""
    format: str = Field("json", description="Formato de exportación")
    include_metadata: bool = Field(True, description="Incluir metadatos")
    include_raw_data: bool = Field(False, description="Incluir datos raw")
    date_from: Optional[datetime] = Field(None, description="Fecha desde")
    date_to: Optional[datetime] = Field(None, description="Fecha hasta")
    
    @field_validator('format')
    @classmethod
    def validate_format(cls, v):
        """Validar formato de exportación"""
        valid_formats = ['json', 'csv', 'xlsx', 'pdf']
        if v not in valid_formats:
            raise ValueError(f"Formato no válido. Debe ser uno de: {valid_formats}")
        return v
    
    @model_validator(mode='after')
    def validate_date_range(self):
        """Validar rango de fechas"""
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError("date_from debe ser anterior a date_to")
        return self
