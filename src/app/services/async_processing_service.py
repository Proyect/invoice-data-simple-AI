import asyncio
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import redis
from rq import Queue, Worker
from rq import connections as rq_connections
from rq.job import Job
import json
from app.core.config import settings
from app.core.database import get_db
from app.models.document import Document

logger = logging.getLogger(__name__)

class ProcessingStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class ProcessingJob:
    id: str
    status: ProcessingStatus
    progress: int
    result: Optional[Dict[str, Any]]
    error: Optional[str]
    created_at: str
    updated_at: str

class AsyncProcessingService:
    """
    Servicio de procesamiento asíncrono usando Redis Queue
    """
    
    def __init__(self):
        # Configurar Redis
        try:
            self.redis_conn = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB
            )
            self.queue = Queue(settings.RQ_QUEUE_NAME, connection=self.redis_conn)
            logger.info("Redis Queue inicializado correctamente")
        except Exception as e:
            logger.error(f"Error inicializando Redis Queue: {e}")
            self.redis_conn = None
            self.queue = None
        
        # Servicios
        from app.services.optimal_ocr_service import OptimalOCRService
        from app.services.intelligent_extraction_service import IntelligentExtractionService
        
        self.ocr_service = OptimalOCRService()
        self.extraction_service = IntelligentExtractionService()
    
    async def process_document_async(self, image_path: str, document_type: str = None, document_id: int = None) -> str:
        """
        Inicia procesamiento asíncrono de documento
        """
        
        if not self.queue:
            raise Exception("Redis Queue no disponible")
        
        try:
            # Crear trabajo
            job = self.queue.enqueue(
                self._process_document_worker,
                image_path,
                document_type,
                document_id,
                job_timeout=settings.RQ_WORKER_TIMEOUT
            )
            
            logger.info(f"Trabajo creado: {job.id}")
            return job.id
            
        except Exception as e:
            logger.error(f"Error creando trabajo: {e}")
            raise
    
    async def get_job_status(self, job_id: str) -> ProcessingJob:
        """
        Obtiene estado del trabajo
        """
        
        if not self.redis_conn:
            return ProcessingJob(
                id=job_id,
                status=ProcessingStatus.FAILED,
                progress=0,
                result=None,
                error="Redis no disponible",
                created_at="",
                updated_at=""
            )
        
        try:
            job = Job.fetch(job_id, connection=self.redis_conn)
            
            # Determinar estado
            if job.is_finished:
                status = ProcessingStatus.COMPLETED
                progress = 100
                result = job.result
                error = None
            elif job.is_failed:
                status = ProcessingStatus.FAILED
                progress = 0
                result = None
                error = str(job.exc_info) if job.exc_info else "Error desconocido"
            elif job.is_started:
                status = ProcessingStatus.PROCESSING
                progress = 50
                result = None
                error = None
            else:
                status = ProcessingStatus.PENDING
                progress = 0
                result = None
                error = None
            
            return ProcessingJob(
                id=job_id,
                status=status,
                progress=progress,
                result=result,
                error=error,
                created_at=job.created_at.isoformat() if job.created_at else "",
                updated_at=job.updated_at.isoformat() if job.updated_at else ""
            )
            
        except Exception as e:
            logger.error(f"Error obteniendo estado del trabajo: {e}")
            return ProcessingJob(
                id=job_id,
                status=ProcessingStatus.FAILED,
                progress=0,
                result=None,
                error=str(e),
                created_at="",
                updated_at=""
            )
    
    def _process_document_worker(self, image_path: str, document_type: str = None, document_id: int = None) -> Dict[str, Any]:
        """
        Worker para procesar documentos (se ejecuta en background)
        """
        
        try:
            logger.info(f"Procesando documento: {image_path}")
            
            # Paso 1: OCR
            ocr_result = asyncio.run(self.ocr_service.extract_text_optimal(image_path, document_type))
            
            # Paso 2: Extracción de datos
            extraction_result = asyncio.run(
                self.extraction_service.extract_intelligent_data(
                    ocr_result.text,
                    image_path
                )
            )
            
            # Paso 3: Actualizar base de datos si se proporciona document_id
            if document_id:
                self._update_document_in_db(document_id, ocr_result, extraction_result)
            
            # Paso 4: Combinar resultados
            final_result = {
                'ocr': {
                    'text': ocr_result.text,
                    'confidence': ocr_result.confidence,
                    'provider': ocr_result.provider,
                    'cost': ocr_result.cost,
                    'processing_time': ocr_result.processing_time
                },
                'extraction': {
                    'document_type': extraction_result.document_type.value,
                    'confidence': extraction_result.confidence,
                    'entities': extraction_result.entities,
                    'structured_data': extraction_result.structured_data,
                    'metadata': extraction_result.metadata
                },
                'metadata': {
                    'total_processing_time': ocr_result.processing_time,
                    'image_path': image_path,
                    'document_type': document_type,
                    'document_id': document_id
                }
            }
            
            logger.info(f"Documento procesado exitosamente: {image_path}")
            return final_result
            
        except Exception as e:
            logger.error(f"Error procesando documento {image_path}: {e}")
            # Actualizar estado en base de datos si hay error
            if document_id:
                self._update_document_error(document_id, str(e))
            raise
    
    def _update_document_in_db(self, document_id: int, ocr_result, extraction_result):
        """Actualiza documento en base de datos con resultados"""
        try:
            from sqlalchemy.orm import sessionmaker
            from app.core.database import engine
            
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            db = SessionLocal()
            
            try:
                document = db.query(Document).filter(Document.id == document_id).first()
                if document:
                    document.raw_text = ocr_result.text
                    document.extracted_data = {
                        'document_type': extraction_result.document_type.value,
                        'confidence': extraction_result.confidence,
                        'entities': extraction_result.entities,
                        'structured_data': extraction_result.structured_data,
                        'metadata': extraction_result.metadata
                    }
                    document.confidence_score = int(extraction_result.confidence * 100)
                    document.ocr_provider = ocr_result.provider
                    document.ocr_cost = str(ocr_result.cost)
                    document.processing_time = str(ocr_result.processing_time)
                    
                    db.commit()
                    logger.info(f"Documento {document_id} actualizado en base de datos")
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error actualizando documento en base de datos: {e}")
    
    def _update_document_error(self, document_id: int, error_message: str):
        """Actualiza documento con error"""
        try:
            from sqlalchemy.orm import sessionmaker
            from app.core.database import engine
            
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            db = SessionLocal()
            
            try:
                document = db.query(Document).filter(Document.id == document_id).first()
                if document:
                    document.extracted_data = {
                        'error': error_message,
                        'status': 'failed'
                    }
                    db.commit()
                    logger.info(f"Error guardado para documento {document_id}")
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error guardando error en documento: {e}")
    
    async def get_queue_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de la cola"""
        if not self.queue:
            return {"error": "Queue no disponible"}
        
        try:
            return {
                "queue_name": self.queue.name,
                "pending_jobs": len(self.queue),
                "failed_jobs": len(self.queue.failed_job_registry),
                "finished_jobs": len(self.queue.finished_job_registry),
                "workers": len(self.queue.workers)
            }
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de cola: {e}")
            return {"error": str(e)}
    
    async def retry_failed_job(self, job_id: str) -> bool:
        """Reintenta un trabajo fallido"""
        if not self.redis_conn:
            return False
        
        try:
            job = Job.fetch(job_id, connection=self.redis_conn)
            if job.is_failed:
                job.requeue()
                return True
            return False
        except Exception as e:
            logger.error(f"Error reintentando trabajo {job_id}: {e}")
            return False
