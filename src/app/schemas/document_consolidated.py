"""
Schemas Consolidados de Documentos
==================================

Schemas unificados para documentos con funcionalidades completas.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator

from .base import (
    BaseSchema, TimestampSchema, SoftDeleteSchema, MetadataSchema,
    PaginationSchema, SearchSchema, ResponseSchema, ErrorSchema,
    FileSchema, ConfidenceSchema, ProcessingSchema, TagsSchema
)


# Enums para schemas
class DocumentTypeEnum(str, Enum):
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


class DocumentStatusEnum(str, Enum):
    """Estados del procesamiento del documento"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    REVIEWING = "reviewing"
    APPROVED = "approved"
    REJECTED = "rejected"


class OCRProviderEnum(str, Enum):
    """Proveedores de OCR disponibles"""
    TESSERACT = "tesseract"
    GOOGLE_VISION = "google_vision"
    AWS_TEXTRACT = "aws_textract"
    AZURE_OCR = "azure_ocr"
    HYBRID = "hybrid"


class ExtractionMethodEnum(str, Enum):
    """Métodos de extracción de datos"""
    REGEX = "regex"
    SPACY = "spacy"
    LLM = "llm"
    HYBRID = "hybrid"
    MANUAL = "manual"


# Schemas base
class DocumentBaseSchema(BaseSchema, FileSchema):
    """Schema base para documentos"""
    document_type: Optional[DocumentTypeEnum] = Field(None, description="Tipo de documento")
    language: str = Field("es", max_length=10, description="Idioma del documento")
    priority: int = Field(5, ge=1, le=10, description="Prioridad de procesamiento (1=alta, 10=baja)")


class DocumentCreateSchema(DocumentBaseSchema):
    """Schema para crear documentos"""
    file_path: str = Field(..., min_length=1, max_length=500, description="Ruta del archivo")
    organization_id: Optional[int] = Field(None, description="ID de la organización")
    user_id: Optional[int] = Field(None, description="ID del usuario")
    tags: List[str] = Field(default_factory=list, description="Tags del documento")
    
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


class DocumentUpdateSchema(BaseSchema):
    """Schema para actualizar documentos"""
    document_type: Optional[DocumentTypeEnum] = None
    status: Optional[DocumentStatusEnum] = None
    priority: Optional[int] = Field(None, ge=1, le=10)
    language: Optional[str] = Field(None, max_length=10)
    raw_text: Optional[str] = None
    extracted_data: Optional[Dict[str, Any]] = None
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    quality_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    ocr_provider: Optional[OCRProviderEnum] = None
    extraction_method: Optional[ExtractionMethodEnum] = None
    ocr_cost: Optional[float] = Field(None, ge=0.0)
    processing_time_seconds: Optional[float] = Field(None, ge=0.0)
    page_count: Optional[int] = Field(None, ge=0)
    word_count: Optional[int] = Field(None, ge=0)
    review_notes: Optional[str] = None
    tags: Optional[List[str]] = None
    organization_id: Optional[int] = None
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        """Validar tags en actualización"""
        if v is not None:
            if len(v) > 20:
                raise ValueError("No se pueden tener más de 20 tags")
            
            for tag in v:
                if not tag or len(tag.strip()) == 0:
                    raise ValueError("Los tags no pueden estar vacíos")
                if len(tag) > 100:
                    raise ValueError("Cada tag no puede tener más de 100 caracteres")
            
            return [tag.strip().lower() for tag in v]
        return v


class DocumentResponseSchema(DocumentBaseSchema, TimestampSchema, SoftDeleteSchema, MetadataSchema, ConfidenceSchema, ProcessingSchema, TagsSchema):
    """Schema de respuesta para documentos"""
    id: int = Field(..., description="ID del documento")
    uuid: str = Field(..., description="UUID del documento")
    file_path: str = Field(..., description="Ruta del archivo")
    status: DocumentStatusEnum = Field(..., description="Estado del documento")
    raw_text: Optional[str] = Field(None, description="Texto extraído por OCR")
    extracted_data: Optional[Dict[str, Any]] = Field(None, description="Datos estructurados extraídos")
    ocr_provider: Optional[OCRProviderEnum] = Field(None, description="Proveedor OCR utilizado")
    extraction_method: Optional[ExtractionMethodEnum] = Field(None, description="Método de extracción utilizado")
    user_id: Optional[int] = Field(None, description="ID del usuario propietario")
    organization_id: Optional[int] = Field(None, description="ID de la organización")
    reviewed_by: Optional[int] = Field(None, description="ID del revisor")
    review_notes: Optional[str] = Field(None, description="Notas de revisión")
    processed_at: Optional[datetime] = Field(None, description="Fecha de procesamiento")
    reviewed_at: Optional[datetime] = Field(None, description="Fecha de revisión")
    
    # Campos calculados
    file_size_mb: Optional[float] = Field(None, description="Tamaño del archivo en MB")
    is_processed: bool = Field(..., description="Indica si el documento fue procesado")
    needs_review: bool = Field(..., description="Indica si necesita revisión manual")
    
    @model_validator(mode='after')
    def calculate_computed_fields(self):
        """Calcular campos computados"""
        # Calcular tamaño en MB
        if self.file_size:
            self.file_size_mb = round(self.file_size / (1024 * 1024), 2)
        
        # Determinar si está procesado
        self.is_processed = self.status in [DocumentStatusEnum.PROCESSED, DocumentStatusEnum.APPROVED]
        
        # Determinar si necesita revisión
        self.needs_review = (
            self.status == DocumentStatusEnum.REVIEWING or
            (self.confidence_score is not None and self.confidence_score < 0.7) or
            self.status == DocumentStatusEnum.FAILED
        )
        
        return self


class DocumentListResponseSchema(BaseSchema, PaginationSchema):
    """Schema para listado de documentos"""
    documents: List[DocumentResponseSchema] = Field(..., description="Lista de documentos")


class DocumentSearchRequestSchema(SearchSchema):
    """Schema para búsqueda de documentos"""
    document_type: Optional[DocumentTypeEnum] = None
    status: Optional[DocumentStatusEnum] = None
    ocr_provider: Optional[OCRProviderEnum] = None
    min_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    max_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    tags: Optional[List[str]] = None
    organization_id: Optional[int] = None
    user_id: Optional[int] = None
    
    @model_validator(mode='after')
    def validate_confidence_and_date_ranges(self):
        """Validar rangos de confianza y fechas"""
        if self.max_confidence is not None and self.min_confidence is not None:
            if self.max_confidence < self.min_confidence:
                raise ValueError("max_confidence debe ser mayor o igual a min_confidence")
        
        if self.date_to is not None and self.date_from is not None:
            if self.date_to < self.date_from:
                raise ValueError("date_to debe ser mayor o igual a date_from")
        
        return self


class DocumentStatsResponseSchema(BaseSchema):
    """Schema para estadísticas de documentos"""
    total_documents: int = Field(..., description="Total de documentos")
    by_status: Dict[str, int] = Field(..., description="Conteo por estado")
    by_type: Dict[str, int] = Field(..., description="Conteo por tipo")
    by_ocr_provider: Dict[str, int] = Field(..., description="Conteo por proveedor OCR")
    by_month: Dict[str, int] = Field(..., description="Conteo por mes")
    average_confidence: float = Field(..., description="Confianza promedio")
    total_processing_time: float = Field(..., description="Tiempo total de procesamiento")
    total_storage_mb: float = Field(..., description="Almacenamiento total en MB")


class DocumentProcessingRequestSchema(BaseSchema):
    """Schema para solicitar procesamiento de documento"""
    document_id: int = Field(..., description="ID del documento")
    ocr_provider: Optional[OCRProviderEnum] = None
    extraction_method: Optional[ExtractionMethodEnum] = None
    force_reprocess: bool = Field(False, description="Forzar reprocesamiento")
    priority: int = Field(5, ge=1, le=10, description="Prioridad de procesamiento")


class DocumentReviewRequestSchema(BaseSchema):
    """Schema para revisar documento"""
    document_id: int = Field(..., description="ID del documento")
    action: str = Field(..., pattern="^(approve|reject|request_changes)$", description="Acción a realizar")
    review_notes: Optional[str] = Field(None, description="Notas de revisión")
    confidence_override: Optional[float] = Field(None, ge=0.0, le=1.0, description="Sobrescribir confianza")


class DocumentBatchOperationRequestSchema(BaseSchema):
    """Schema para operaciones en lote"""
    document_ids: List[int] = Field(..., min_items=1, max_items=100, description="IDs de documentos")
    operation: str = Field(..., pattern="^(delete|update_status|update_type|add_tags|remove_tags|approve|reject)$", description="Operación a realizar")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Parámetros de la operación")


class DocumentExportRequestSchema(BaseSchema):
    """Schema para exportar documentos"""
    document_ids: Optional[List[int]] = Field(None, description="IDs específicos de documentos")
    filters: Optional[DocumentSearchRequestSchema] = Field(None, description="Filtros de búsqueda")
    format: str = Field("json", pattern="^(json|csv|xlsx|pdf)$", description="Formato de exportación")
    include_extracted_data: bool = Field(True, description="Incluir datos extraídos")
    include_raw_text: bool = Field(False, description="Incluir texto raw")


# Schemas de respuesta específicos
class DocumentCreateResponseSchema(ResponseSchema):
    """Schema de respuesta para creación de documentos"""
    data: DocumentResponseSchema = Field(..., description="Documento creado")


class DocumentUpdateResponseSchema(ResponseSchema):
    """Schema de respuesta para actualización de documentos"""
    data: DocumentResponseSchema = Field(..., description="Documento actualizado")


class DocumentDeleteResponseSchema(ResponseSchema):
    """Schema de respuesta para eliminación de documentos"""
    message: str = Field("Documento eliminado exitosamente", description="Mensaje de confirmación")


class DocumentProcessingResponseSchema(ResponseSchema):
    """Schema de respuesta para procesamiento de documentos"""
    data: Dict[str, Any] = Field(..., description="Información del procesamiento")
    job_id: Optional[str] = Field(None, description="ID del trabajo de procesamiento")
    estimated_time: Optional[str] = Field(None, description="Tiempo estimado de procesamiento")


class DocumentReviewResponseSchema(ResponseSchema):
    """Schema de respuesta para revisión de documentos"""
    data: DocumentResponseSchema = Field(..., description="Documento actualizado")
    message: str = Field(..., description="Mensaje de confirmación")


class DocumentBatchOperationResponseSchema(ResponseSchema):
    """Schema de respuesta para operaciones en lote"""
    data: Dict[str, Any] = Field(..., description="Resultado de la operación")
    processed_count: int = Field(..., description="Número de documentos procesados")
    failed_count: int = Field(..., description="Número de documentos que fallaron")


class DocumentExportResponseSchema(ResponseSchema):
    """Schema de respuesta para exportación de documentos"""
    data: Dict[str, Any] = Field(..., description="Información de la exportación")
    download_url: Optional[str] = Field(None, description="URL de descarga")
    file_size: Optional[int] = Field(None, description="Tamaño del archivo exportado")
