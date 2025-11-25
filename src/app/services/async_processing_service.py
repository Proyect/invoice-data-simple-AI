import asyncio
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import redis
from rq import Queue, Worker, Connection
from rq.job import Job
import json
from ..core.config import settings
from ..core.environment import get_settings
from ..core.database import get_db
from ..models.document import Document

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
    
    def __init__(
        self,
        ocr_service=None,
        extraction_service=None,
        redis_conn=None,
        queue=None
    ):
        """
        Inicializar servicio con dependencias inyectadas.
        
        Args:
            ocr_service: Instancia de OptimalOCRService (opcional)
            extraction_service: Instancia de IntelligentExtractionService (opcional)
            redis_conn: Conexión Redis (opcional)
            queue: Cola RQ (opcional)
        """
        # Inyectar servicios o crear instancias si no se proporcionan
        if ocr_service is None:
            from ..services.optimal_ocr_service import OptimalOCRService
            ocr_service = OptimalOCRService()
        
        if extraction_service is None:
            from ..services.intelligent_extraction_service import IntelligentExtractionService
            extraction_service = IntelligentExtractionService()
        
        self.ocr_service = ocr_service
        self.extraction_service = extraction_service
        
        # Configurar Redis si no se proporciona
        if redis_conn is None or queue is None:
            try:
                env_settings = get_settings()
                redis_config = env_settings.redis
                
                if redis_conn is None:
                    self.redis_conn = redis.Redis(
                        host=redis_config.host,
                        port=redis_config.port,
                        db=redis_config.db,
                        password=redis_config.password,
                        decode_responses=False  # RQ necesita bytes
                    )
                else:
                    self.redis_conn = redis_conn
                
                if queue is None:
                    self.queue = Queue(env_settings.rq_queue_name, connection=self.redis_conn)
                else:
                    self.queue = queue
                
                logger.info(f"Redis Queue inicializado correctamente en {redis_config.host}:{redis_config.port}")
            except Exception as e:
                logger.error(f"Error inicializando Redis Queue: {e}")
                self.redis_conn = redis_conn
                self.queue = queue
        else:
            self.redis_conn = redis_conn
            self.queue = queue
    
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
            
            # Actualizar estado a "processing" si hay document_id
            if document_id:
                self._update_document_status(document_id, "processing")
            
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
            from ..core.database import engine
            
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            db = SessionLocal()
            
            try:
                document = db.query(Document).filter(Document.id == document_id).first()
                if document:
                    document.raw_text = ocr_result.text
                    
                    # Función para aplanar datos de forma robusta
                    def prepare_extracted_data(extraction_result):
                        """Prepara extracted_data para guardar en BD"""
                        # Para facturas, siempre aplanar structured_data
                        if extraction_result.document_type.value == 'factura':
                            if extraction_result.structured_data and isinstance(extraction_result.structured_data, dict):
                                # Copiar structured_data como base
                                extracted_data = extraction_result.structured_data.copy()
                                
                                # Asegurar campos básicos
                                extracted_data['document_type'] = 'factura'
                                extracted_data['confidence'] = extraction_result.confidence
                                
                                # Agregar metadata si existe
                                if extraction_result.metadata:
                                    extracted_data['metadata'] = extraction_result.metadata
                                
                                # Validar que no esté vacío
                                if not extracted_data or len(extracted_data) <= 2:  # Solo document_type y confidence
                                    logger.warning(f"Documento {document_id}: structured_data parece vacío o incompleto")
                                    # Intentar usar entities como fallback
                                    if extraction_result.entities:
                                        extracted_data['entities'] = extraction_result.entities
                                
                                logger.info(f"Documento {document_id}: Guardando extracted_data con {len(extracted_data)} campos")
                                return extracted_data
                            else:
                                logger.warning(f"Documento {document_id}: No hay structured_data para factura")
                                # Fallback: crear estructura básica
                                return {
                                    'document_type': 'factura',
                                    'confidence': extraction_result.confidence,
                                    'entities': extraction_result.entities if extraction_result.entities else {},
                                    'metadata': extraction_result.metadata if extraction_result.metadata else {}
                                }
                        else:
                            # Para otros documentos, mantener estructura anidada pero asegurar que tenga contenido
                            structured_data = extraction_result.structured_data if extraction_result.structured_data else {}
                            return {
                                'document_type': extraction_result.document_type.value if hasattr(extraction_result.document_type, 'value') else str(extraction_result.document_type),
                                'confidence': extraction_result.confidence,
                                'entities': extraction_result.entities if extraction_result.entities else {},
                                'structured_data': structured_data,
                                'metadata': extraction_result.metadata if extraction_result.metadata else {}
                            }
                    
                    # Preparar datos
                    extracted_data = prepare_extracted_data(extraction_result)
                    
                    # Validar antes de guardar
                    if not extracted_data or (isinstance(extracted_data, dict) and len(extracted_data) == 0):
                        logger.error(f"Documento {document_id}: extracted_data está vacío, no se guardará")
                    else:
                        document.extracted_data = extracted_data
                        logger.info(f"Documento {document_id}: extracted_data guardado correctamente con {len(extracted_data) if isinstance(extracted_data, dict) else 0} campos")
                    document.confidence_score = int(extraction_result.confidence * 100) if extraction_result.confidence else None
                    document.ocr_provider = ocr_result.provider if hasattr(ocr_result, 'provider') else 'tesseract'
                    # Convertir ocr_cost a float (la base de datos espera double precision)
                    ocr_cost_value = ocr_result.cost if hasattr(ocr_result, 'cost') else 0.0
                    document.ocr_cost = float(ocr_cost_value) if ocr_cost_value is not None else 0.0
                    # processing_time como string (VARCHAR)
                    processing_time_value = ocr_result.processing_time if hasattr(ocr_result, 'processing_time') else 0.0
                    document.processing_time = str(processing_time_value) if processing_time_value is not None else "0"
                    # Actualizar estado a "completed" cuando se procesa exitosamente
                    document.status = "completed"
                    
                    db.commit()
                    logger.info(f"Documento {document_id} actualizado en base de datos")
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error actualizando documento en base de datos: {e}")
    
    def _update_document_status(self, document_id: int, status: str):
        """Actualiza el estado de un documento"""
        try:
            from sqlalchemy.orm import sessionmaker
            from ..core.database import engine
            
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            db = SessionLocal()
            
            try:
                document = db.query(Document).filter(Document.id == document_id).first()
                if document:
                    document.status = status
                    db.commit()
                    logger.info(f"Estado del documento {document_id} actualizado a: {status}")
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error actualizando estado del documento: {e}")
    
    def _update_document_error(self, document_id: int, error_message: str):
        """Actualiza documento con error"""
        try:
            from sqlalchemy.orm import sessionmaker
            from ..core.database import engine
            
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            db = SessionLocal()
            
            try:
                document = db.query(Document).filter(Document.id == document_id).first()
                if document:
                    document.status = "failed"
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
