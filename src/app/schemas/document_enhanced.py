"""
Schemas Pydantic para Documentos Mejorados
Incluye validaciones avanzadas y tipos específicos
"""
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime
from typing import Optional, Dict, Any, List, Union
from enum import Enum
import re

# ============================================================================
# ENUMS PARA SCHEMAS
# ============================================================================

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

# ============================================================================
# SCHEMAS BASE
# ============================================================================

class DocumentEnhancedBase(BaseModel):
    """Schema base para documentos mejorados"""
    filename: str = Field(..., min_length=1, max_length=255, description="Nombre del archivo")
    original_filename: str = Field(..., min_length=1, max_length=255, description="Nombre original del archivo")
    mime_type: Optional[str] = Field(None, max_length=100, description="Tipo MIME del archivo")
    file_size: Optional[int] = Field(None, ge=0, description="Tamaño del archivo en bytes")
    
    @field_validator('filename', 'original_filename')
    @classmethod
    def validate_filename(cls, v):
        """Validar que el nombre del archivo no contenga caracteres peligrosos"""
        if not v or v.strip() == "":
            raise ValueError("El nombre del archivo no puede estar vacío")
        
        # Caracteres peligrosos
        dangerous_chars = ['..', '/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in dangerous_chars:
            if char in v:
                raise ValueError(f"El nombre del archivo no puede contener '{char}'")
        
        return v.strip()

# ============================================================================
# SCHEMAS DE CREACIÓN
# ============================================================================

class DocumentEnhancedCreate(DocumentEnhancedBase):
    """Schema para crear documentos mejorados"""
    file_path: str = Field(..., min_length=1, max_length=500, description="Ruta del archivo")
    document_type: Optional[DocumentTypeEnum] = Field(None, description="Tipo de documento")
    priority: int = Field(default=5, ge=1, le=10, description="Prioridad de procesamiento (1=alta, 10=baja)")
    language: str = Field(default="es", max_length=10, description="Idioma del documento")
    organization_id: Optional[int] = Field(None, description="ID de la organización")
    tags: List[str] = Field(default_factory=list, description="Tags/etiquetas del documento")
    
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

class DocumentEnhancedUpdate(BaseModel):
    """Schema para actualizar documentos mejorados"""
    document_type: Optional[DocumentTypeEnum] = None
    status: Optional[DocumentStatusEnum] = None
    priority: Optional[int] = Field(None, ge=1, le=10)
    raw_text: Optional[str] = None
    extracted_data: Optional[Dict[str, Any]] = None
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    quality_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    ocr_provider: Optional[OCRProviderEnum] = None
    extraction_method: Optional[ExtractionMethodEnum] = None
    ocr_cost: Optional[float] = Field(None, ge=0.0)
    processing_time_seconds: Optional[float] = Field(None, ge=0.0)
    language: Optional[str] = Field(None, max_length=10)
    page_count: Optional[int] = Field(None, ge=0)
    word_count: Optional[int] = Field(None, ge=0)
    review_notes: Optional[str] = None
    tags: Optional[List[str]] = None
    
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

# ============================================================================
# SCHEMAS DE RESPUESTA
# ============================================================================

class DocumentEnhancedResponse(DocumentEnhancedBase):
    """Schema de respuesta para documentos mejorados"""
    id: int
    uuid: str
    file_path: str
    document_type: Optional[DocumentTypeEnum]
    status: DocumentStatusEnum
    priority: int
    raw_text: Optional[str]
    extracted_data: Optional[Dict[str, Any]]
    confidence_score: Optional[float]
    quality_score: Optional[float]
    ocr_provider: Optional[OCRProviderEnum]
    extraction_method: Optional[ExtractionMethodEnum]
    ocr_cost: float
    processing_time_seconds: Optional[float]
    language: str
    page_count: Optional[int]
    word_count: Optional[int]
    user_id: Optional[int]
    organization_id: Optional[int]
    reviewed_by: Optional[int]
    review_notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    processed_at: Optional[datetime]
    reviewed_at: Optional[datetime]
    is_deleted: bool
    deleted_at: Optional[datetime]
    
    # Campos calculados
    file_size_mb: Optional[float] = Field(None, description="Tamaño del archivo en MB")
    is_processed: bool = Field(description="Indica si el documento fue procesado")
    needs_review: bool = Field(description="Indica si necesita revisión manual")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class DocumentEnhancedListResponse(BaseModel):
    """Schema para listado de documentos mejorados"""
    documents: List[DocumentEnhancedResponse]
    total: int = Field(description="Total de documentos")
    page: int = Field(ge=1, description="Página actual")
    size: int = Field(ge=1, le=100, description="Tamaño de página")
    total_pages: int = Field(description="Total de páginas")
    has_next: bool = Field(description="Tiene página siguiente")
    has_prev: bool = Field(description="Tiene página anterior")

# ============================================================================
# SCHEMAS ESPECIALIZADOS
# ============================================================================

class DocumentProcessingRequest(BaseModel):
    """Schema para solicitar procesamiento de documento"""
    document_id: int
    ocr_provider: Optional[OCRProviderEnum] = None
    extraction_method: Optional[ExtractionMethodEnum] = None
    force_reprocess: bool = Field(default=False, description="Forzar reprocesamiento")
    priority: int = Field(default=5, ge=1, le=10)

class DocumentReviewRequest(BaseModel):
    """Schema para revisar documento"""
    document_id: int
    action: str = Field(..., pattern="^(approve|reject|request_changes)$")
    review_notes: Optional[str] = None
    confidence_override: Optional[float] = Field(None, ge=0.0, le=1.0)

class DocumentSearchRequest(BaseModel):
    """Schema para búsqueda de documentos"""
    query: Optional[str] = Field(None, max_length=500)
    document_type: Optional[DocumentTypeEnum] = None
    status: Optional[DocumentStatusEnum] = None
    ocr_provider: Optional[OCRProviderEnum] = None
    min_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    max_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    tags: Optional[List[str]] = None
    organization_id: Optional[int] = None
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)
    sort_by: str = Field(default="created_at", pattern="^(created_at|updated_at|filename|confidence_score)$")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")
    
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

class DocumentStatsResponse(BaseModel):
    """Schema para estadísticas de documentos"""
    total_documents: int
    by_status: Dict[str, int]
    by_type: Dict[str, int]
    by_ocr_provider: Dict[str, int]
    by_month: Dict[str, int]
    average_confidence: float
    total_processing_time: float
    total_storage_mb: float

class DocumentBatchOperationRequest(BaseModel):
    """Schema para operaciones en lote"""
    document_ids: List[int] = Field(..., min_items=1, max_items=100)
    operation: str = Field(..., pattern="^(delete|update_status|update_type|add_tags|remove_tags)$")
    parameters: Optional[Dict[str, Any]] = None

class DocumentExportRequest(BaseModel):
    """Schema para exportar documentos"""
    document_ids: Optional[List[int]] = None
    filters: Optional[DocumentSearchRequest] = None
    format: str = Field(default="json", pattern="^(json|csv|xlsx|pdf)$")
    include_extracted_data: bool = Field(default=True)
    include_raw_text: bool = Field(default=False)

# ============================================================================
# SCHEMAS DE COMPATIBILIDAD
# ============================================================================

class DocumentLegacyToEnhanced(BaseModel):
    """Schema para convertir documentos legacy a mejorados"""
    legacy_document: Dict[str, Any]
    organization_id: Optional[int] = None
    user_id: Optional[int] = None
    tags: List[str] = Field(default_factory=list)
    
    @model_validator(mode='after')
    def validate_legacy_document(self):
        """Validar que el documento legacy tenga campos mínimos"""
        if not self.legacy_document:
            raise ValueError("legacy_document es requerido")
        
        required_fields = ['filename', 'original_filename', 'file_path']
        for field in required_fields:
            if field not in self.legacy_document or not self.legacy_document[field]:
                raise ValueError(f"Campo '{field}' es requerido en legacy_document")
        
        return self

class DocumentEnhancedToLegacy(BaseModel):
    """Schema para convertir documentos mejorados a legacy"""
    enhanced_document: DocumentEnhancedResponse
    include_extracted_data: bool = Field(default=True)
    
    def to_legacy_dict(self) -> Dict[str, Any]:
        """Convierte a formato legacy"""
        doc = self.enhanced_document
        
        legacy_data = {
            "id": doc.id,
            "filename": doc.filename,
            "original_filename": doc.original_filename,
            "file_path": doc.file_path,
            "file_size": doc.file_size,
            "mime_type": doc.mime_type,
            "created_at": doc.created_at,
            "updated_at": doc.updated_at,
        }
        
        if self.include_extracted_data:
            legacy_data.update({
                "raw_text": doc.raw_text,
                "extracted_data": doc.extracted_data,
                "confidence_score": doc.confidence_score,
                "ocr_provider": doc.ocr_provider.value if doc.ocr_provider else None,
                "processing_time": doc.processing_time_seconds,
            })
        
        return legacy_data