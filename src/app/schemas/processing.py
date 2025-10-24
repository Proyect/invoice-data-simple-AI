"""
Schemas Pydantic para Procesamiento Asíncrono
Incluye jobs, steps y tracking de procesamiento
"""
from pydantic import BaseModel, Field, validator, root_validator
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

# ============================================================================
# ENUMS PARA SCHEMAS
# ============================================================================

class JobStatusEnum(str, Enum):
    """Estados de los jobs de procesamiento"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"
    RETRY = "retry"

class JobTypeEnum(str, Enum):
    """Tipos de jobs de procesamiento"""
    DOCUMENT_OCR = "document_ocr"
    DOCUMENT_EXTRACTION = "document_extraction"
    DOCUMENT_CLASSIFICATION = "document_classification"
    BATCH_PROCESSING = "batch_processing"
    DATA_EXPORT = "data_export"
    CLEANUP = "cleanup"
    BACKUP = "backup"
    REPORT_GENERATION = "report_generation"

class StepStatusEnum(str, Enum):
    """Estados de los pasos de procesamiento"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

# ============================================================================
# SCHEMAS BASE
# ============================================================================

class ProcessingJobBase(BaseModel):
    """Schema base para jobs de procesamiento"""
    job_type: JobTypeEnum = Field(..., description="Tipo de job")
    priority: int = Field(default=5, ge=1, le=10, description="Prioridad (1=alta, 10=baja)")
    
    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v):
        """Validar prioridad"""
        if v < 1 or v > 10:
            raise ValueError("La prioridad debe estar entre 1 y 10")
        return v

# ============================================================================
# SCHEMAS DE CREACIÓN
# ============================================================================

class ProcessingJobCreate(ProcessingJobBase):
    """Schema para crear jobs de procesamiento"""
    document_id: Optional[int] = Field(None, description="ID del documento a procesar")
    organization_id: Optional[int] = Field(None, description="ID de la organización")
    input_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Datos de entrada")
    configuration: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Configuración del job")
    timeout_seconds: Optional[int] = Field(None, ge=60, le=3600, description="Timeout en segundos")
    max_retries: int = Field(default=3, ge=0, le=10, description="Máximo número de reintentos")
    
    @field_validator('timeout_seconds')
    @classmethod
    def validate_timeout(cls, v):
        """Validar timeout"""
        if v is not None and v < 60:
            raise ValueError("El timeout mínimo es 60 segundos")
        return v

class ProcessingJobUpdate(BaseModel):
    """Schema para actualizar jobs de procesamiento"""
    status: Optional[JobStatusEnum] = None
    priority: Optional[int] = Field(None, ge=1, le=10)
    progress_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    processing_time_seconds: Optional[float] = Field(None, ge=0.0)
    worker_id: Optional[str] = None
    worker_hostname: Optional[str] = None

    @field_validator('progress_percentage')
    @classmethod
    def validate_progress(cls, v):
        """Validar porcentaje de progreso"""
        if v is not None and (v < 0.0 or v > 100.0):
            raise ValueError("El progreso debe estar entre 0 y 100")
        return v

# ============================================================================
# SCHEMAS DE RESPUESTA
# ============================================================================

class ProcessingJobResponse(ProcessingJobBase):
    """Schema de respuesta para jobs de procesamiento"""
    id: int
    job_id: str
    status: JobStatusEnum
    document_id: Optional[int]
    organization_id: Optional[int]
    user_id: Optional[int]
    input_data: Optional[Dict[str, Any]]
    configuration: Optional[Dict[str, Any]]
    output_data: Optional[Dict[str, Any]]
    error_message: Optional[str]
    error_details: Optional[Dict[str, Any]]
    progress_percentage: float
    processing_time_seconds: Optional[float]
    worker_id: Optional[str]
    worker_hostname: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    updated_at: Optional[datetime]
    retry_count: int
    max_retries: int
    next_retry_at: Optional[datetime]
    timeout_seconds: Optional[int]
    
    # Campos calculados
    is_running: bool = Field(description="Indica si el job está ejecutándose")
    is_completed: bool = Field(description="Indica si el job está completado")
    estimated_remaining_time: Optional[int] = Field(None, description="Tiempo estimado restante en segundos")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class ProcessingJobListResponse(BaseModel):
    """Schema para listado de jobs de procesamiento"""
    jobs: List[ProcessingJobResponse]
    total: int = Field(description="Total de jobs")
    page: int = Field(ge=1, description="Página actual")
    size: int = Field(ge=1, le=100, description="Tamaño de página")
    total_pages: int = Field(description="Total de páginas")
    has_next: bool = Field(description="Tiene página siguiente")
    has_prev: bool = Field(description="Tiene página anterior")

# ============================================================================
# SCHEMAS DE PASOS DE PROCESAMIENTO
# ============================================================================

class ProcessingStepCreate(BaseModel):
    """Schema para crear pasos de procesamiento"""
    job_id: str = Field(..., description="ID del job padre")
    step_name: str = Field(..., min_length=1, max_length=100, description="Nombre del paso")
    step_type: str = Field(..., min_length=1, max_length=50, description="Tipo de paso")
    configuration: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Configuración del paso")
    depends_on: Optional[List[str]] = Field(default_factory=list, description="Pasos de los que depende")
    
    @field_validator('depends_on')
    @classmethod
    def validate_dependencies(cls, v):
        """Validar dependencias"""
        if v is not None and len(v) > 10:
            raise ValueError("No se pueden tener más de 10 dependencias")
        return v

class ProcessingStepUpdate(BaseModel):
    """Schema para actualizar pasos de procesamiento"""
    status: Optional[StepStatusEnum] = None
    progress_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    processing_time_seconds: Optional[float] = Field(None, ge=0.0)

    @field_validator('progress_percentage')
    @classmethod
    def validate_progress(cls, v):
        """Validar porcentaje de progreso"""
        if v is not None and (v < 0.0 or v > 100.0):
            raise ValueError("El progreso debe estar entre 0 y 100")
        return v

class ProcessingStepResponse(BaseModel):
    """Schema de respuesta para pasos de procesamiento"""
    id: int
    job_id: str
    step_name: str
    step_type: str
    status: StepStatusEnum
    configuration: Optional[Dict[str, Any]]
    output_data: Optional[Dict[str, Any]]
    error_message: Optional[str]
    progress_percentage: float
    processing_time_seconds: Optional[float]
    depends_on: List[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

# ============================================================================
# SCHEMAS ESPECIALIZADOS
# ============================================================================

class ProcessingJobSearchRequest(BaseModel):
    """Schema para búsqueda de jobs de procesamiento"""
    job_type: Optional[JobTypeEnum] = None
    status: Optional[JobStatusEnum] = None
    document_id: Optional[int] = None
    organization_id: Optional[int] = None
    user_id: Optional[int] = None
    worker_id: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    min_progress: Optional[float] = Field(None, ge=0.0, le=100.0)
    max_progress: Optional[float] = Field(None, ge=0.0, le=100.0)
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)
    sort_by: str = Field(default="created_at", pattern="^(created_at|started_at|completed_at|priority|progress_percentage)$")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")
    
    @field_validator('date_to')
    @classmethod
    def validate_date_range(cls, v, values):
        """Validar rango de fechas"""
        if v is not None and 'date_from' in values and values['date_from'] is not None:
            if v < values['date_from']:
                raise ValueError("date_to debe ser mayor o igual a date_from")
        return v
    
    @field_validator('max_progress')
    @classmethod
    def validate_progress_range(cls, v, values):
        """Validar rango de progreso"""
        if v is not None and 'min_progress' in values and values['min_progress'] is not None:
            if v < values['min_progress']:
                raise ValueError("max_progress debe ser mayor o igual a min_progress")
        return v

class ProcessingJobStatsResponse(BaseModel):
    """Schema para estadísticas de jobs de procesamiento"""
    total_jobs: int
    by_status: Dict[str, int]
    by_type: Dict[str, int]
    by_worker: Dict[str, int]
    average_processing_time: float
    success_rate: float
    failure_rate: float
    jobs_today: int
    jobs_this_week: int
    jobs_this_month: int

class ProcessingJobCancelRequest(BaseModel):
    """Schema para cancelar jobs"""
    job_ids: List[str] = Field(..., min_items=1, max_items=50, description="IDs de jobs a cancelar")
    reason: Optional[str] = Field(None, max_length=500, description="Razón de cancelación")

class ProcessingJobRetryRequest(BaseModel):
    """Schema para reintentar jobs"""
    job_ids: List[str] = Field(..., min_items=1, max_items=50, description="IDs de jobs a reintentar")
    max_retries: Optional[int] = Field(None, ge=1, le=10, description="Nuevo máximo de reintentos")
    delay_seconds: Optional[int] = Field(None, ge=0, le=3600, description="Delay antes del reintento")

class ProcessingJobBatchRequest(BaseModel):
    """Schema para operaciones en lote"""
    operation: str = Field(..., pattern="^(cancel|retry|delete|update_priority)$", description="Operación a realizar")
    job_ids: List[str] = Field(..., min_items=1, max_items=100, description="IDs de jobs")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Parámetros adicionales")

# ============================================================================
# SCHEMAS DE CONFIGURACIÓN
# ============================================================================

class OCRJobConfiguration(BaseModel):
    """Configuración para jobs de OCR"""
    provider: str = Field(..., pattern="^(tesseract|google_vision|aws_textract|azure_ocr|hybrid)$")
    language: str = Field(default="es", max_length=10)
    confidence_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    preprocess: bool = Field(default=True, description="Preprocesar imagen antes de OCR")
    extract_tables: bool = Field(default=False, description="Extraer tablas del documento")
    extract_layout: bool = Field(default=False, description="Extraer información de layout")

class ExtractionJobConfiguration(BaseModel):
    """Configuración para jobs de extracción"""
    method: str = Field(..., pattern="^(regex|spacy|llm|hybrid|manual)$")
    document_type: str = Field(..., description="Tipo de documento a procesar")
    fields_to_extract: List[str] = Field(..., min_items=1, description="Campos a extraer")
    validation_rules: Optional[Dict[str, Any]] = Field(default_factory=dict)
    confidence_threshold: float = Field(default=0.8, ge=0.0, le=1.0)

class BatchProcessingConfiguration(BaseModel):
    """Configuración para procesamiento en lote"""
    document_ids: List[int] = Field(..., min_items=1, max_items=1000)
    operation: str = Field(..., pattern="^(ocr|extraction|classification|validation)$")
    parallel_workers: int = Field(default=3, ge=1, le=10)
    batch_size: int = Field(default=10, ge=1, le=100)
    stop_on_error: bool = Field(default=False, description="Detener si hay error")

# ============================================================================
# SCHEMAS DE MONITOREO
# ============================================================================

class ProcessingQueueStatus(BaseModel):
    """Schema para estado de colas de procesamiento"""
    queue_name: str
    pending_jobs: int
    running_jobs: int
    completed_jobs: int
    failed_jobs: int
    average_processing_time: float
    workers_active: int
    workers_idle: int
    queue_size: int
    oldest_pending_job: Optional[datetime]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class WorkerStatus(BaseModel):
    """Schema para estado de workers"""
    worker_id: str
    hostname: str
    status: str = Field(..., pattern="^(active|idle|busy|offline)$")
    current_jobs: int
    total_jobs_processed: int
    last_activity: Optional[datetime]
    cpu_usage: Optional[float]
    memory_usage: Optional[float]
    disk_usage: Optional[float]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class ProcessingMetrics(BaseModel):
    """Schema para métricas de procesamiento"""
    time_period: str = Field(..., description="Período de tiempo")
    total_jobs: int
    successful_jobs: int
    failed_jobs: int
    cancelled_jobs: int
    average_processing_time: float
    throughput_per_hour: float
    error_rate: float
    success_rate: float
    by_job_type: Dict[str, int]
    by_hour: Dict[str, int]
    by_day: Dict[str, int]

# ============================================================================
# SCHEMAS DE NOTIFICACIONES
# ============================================================================

class ProcessingNotification(BaseModel):
    """Schema para notificaciones de procesamiento"""
    job_id: str
    user_id: Optional[int]
    organization_id: Optional[int]
    notification_type: str = Field(..., pattern="^(job_started|job_completed|job_failed|job_cancelled|progress_update)$")
    title: str
    message: str
    data: Optional[Dict[str, Any]] = None
    created_at: datetime
    is_read: bool = False
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }