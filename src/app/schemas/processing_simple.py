"""
Schemas Pydantic simplificados para Procesamiento
Versión básica que funciona con Pydantic v2
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

# Enums
class JobStatusEnum(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class JobTypeEnum(str, Enum):
    OCR = "ocr"
    EXTRACTION = "extraction"
    VALIDATION = "validation"
    BATCH = "batch"

# Schemas básicos
class ProcessingJobBase(BaseModel):
    """Schema base para trabajos de procesamiento"""
    job_type: JobTypeEnum
    status: JobStatusEnum = Field(default=JobStatusEnum.PENDING)
    priority: int = Field(default=5, ge=1, le=10)

class ProcessingJobCreate(ProcessingJobBase):
    """Schema para crear trabajos de procesamiento"""
    document_id: Optional[int] = None
    parameters: Optional[Dict[str, Any]] = None

class ProcessingJobUpdate(BaseModel):
    """Schema para actualizar trabajos de procesamiento"""
    status: Optional[JobStatusEnum] = None
    priority: Optional[int] = Field(None, ge=1, le=10)
    parameters: Optional[Dict[str, Any]] = None

class ProcessingJobResponse(ProcessingJobBase):
    """Schema de respuesta para trabajos de procesamiento"""
    id: int
    document_id: Optional[int] = None
    parameters: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Schemas de compatibilidad
class ProcessingJobLegacyToEnhanced(BaseModel):
    """Schema para convertir trabajos legacy a mejorados"""
    legacy_job: Dict[str, Any]
    job_type: JobTypeEnum = Field(default=JobTypeEnum.OCR)

class ProcessingJobEnhancedToLegacy(BaseModel):
    """Schema para convertir trabajos mejorados a legacy"""
    enhanced_job: ProcessingJobResponse
