from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any, List

class DocumentBase(BaseModel):
    filename: str = Field(..., description="Nombre del archivo")
    original_filename: str = Field(..., description="Nombre original del archivo")

class DocumentCreate(DocumentBase):
    file_path: str = Field(..., description="Ruta del archivo")
    file_size: Optional[int] = Field(None, description="Tamaño del archivo en bytes")
    mime_type: Optional[str] = Field(None, description="Tipo MIME del archivo")

class DocumentUpdate(BaseModel):
    raw_text: Optional[str] = Field(None, description="Texto extraído por OCR")
    extracted_data: Optional[Dict[str, Any]] = Field(None, description="Datos estructurados extraídos")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Puntuación de confianza del OCR")
    ocr_provider: Optional[str] = Field(None, description="Proveedor OCR utilizado")
    ocr_cost: Optional[str] = Field(None, description="Costo del OCR")
    processing_time: Optional[str] = Field(None, description="Tiempo de procesamiento")

class DocumentResponse(DocumentBase):
    id: int
    file_path: str
    file_size: Optional[int]
    mime_type: Optional[str]
    raw_text: Optional[str]
    extracted_data: Optional[Dict[str, Any]]
    confidence_score: Optional[float]
    ocr_provider: Optional[str]
    ocr_cost: Optional[str]
    processing_time: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int
    page: int
    size: int

class ExtractedDataResponse(BaseModel):
    document_id: int
    filename: str
    extracted_data: Dict[str, Any]
    raw_text: Optional[str]
    confidence_score: Optional[float]
    ocr_provider: Optional[str] = None
    processing_time: Optional[str] = None

class ProcessingJobResponse(BaseModel):
    id: str
    status: str
    progress: int
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: str
    updated_at: str

class QueueStatsResponse(BaseModel):
    queue_name: str
    pending_jobs: int
    failed_jobs: int
    finished_jobs: int
    workers: int

class DocumentStatsResponse(BaseModel):
    total_documents: int
    by_mime_type: List[Dict[str, Any]]
    by_month: List[Dict[str, Any]]
    by_ocr_provider: List[Dict[str, Any]]
    average_confidence: float

class SearchResultResponse(BaseModel):
    query: str
    results: List[Dict[str, Any]]
    total: int

class BatchUploadResponse(BaseModel):
    processed: int
    errors: int
    results: List[Dict[str, Any]]
    error_details: List[Dict[str, Any]]

class AsyncUploadResponse(BaseModel):
    message: str
    document_id: int
    job_id: str
    status_url: str
    estimated_time: str

class ReprocessResponse(BaseModel):
    message: str
    document_id: int
    job_id: str
    status_url: str
