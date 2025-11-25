"""
Modelos para el procesamiento de documentos y jobs asíncronos
"""
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, Float,
    ForeignKey, Index, func, JSON, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from ..core.database import Base
import enum
from datetime import datetime, timedelta
from typing import Dict, Any, Optional


class JobStatus(enum.Enum):
    """Estados de los jobs de procesamiento"""
    PENDING = "pending"             # En cola, esperando procesamiento
    RUNNING = "running"             # Ejecutándose actualmente
    COMPLETED = "completed"         # Completado exitosamente
    FAILED = "failed"              # Falló con error
    CANCELLED = "cancelled"         # Cancelado por usuario/sistema
    TIMEOUT = "timeout"            # Timeout durante ejecución
    RETRY = "retry"                # Reintentando después de fallo


class JobType(enum.Enum):
    """Tipos de jobs de procesamiento"""
    DOCUMENT_OCR = "document_ocr"                   # OCR de documento
    DOCUMENT_EXTRACTION = "document_extraction"     # Extracción de datos
    DOCUMENT_CLASSIFICATION = "document_classification"  # Clasificación automática
    BATCH_PROCESSING = "batch_processing"           # Procesamiento en lote
    DATA_EXPORT = "data_export"                    # Exportación de datos
    CLEANUP = "cleanup"                            # Limpieza de archivos
    BACKUP = "backup"                              # Backup de datos
    REPORT_GENERATION = "report_generation"         # Generación de reportes


class ProcessingJob(Base):
    """Jobs de procesamiento asíncrono"""
    __tablename__ = "processing_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(36), unique=True, nullable=False, index=True)  # UUID
    
    # Información del job
    job_type = Column(SQLEnum(JobType), nullable=False, index=True)
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING, index=True)
    priority = Column(Integer, default=5, nullable=False)  # 1=alta, 5=normal, 10=baja
    
    # Relaciones
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=True, index=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=True, index=True)
    
    # Configuración del job
    input_data = Column(JSON, nullable=True)        # Datos de entrada
    configuration = Column(JSON, nullable=True)     # Configuración específica
    
    # Resultados
    output_data = Column(JSON, nullable=True)       # Datos de salida
    error_message = Column(Text, nullable=True)     # Mensaje de error si falla
    error_details = Column(JSON, nullable=True)     # Detalles técnicos del error
    
    # Métricas de ejecución
    progress_percentage = Column(Float, default=0.0, nullable=False)
    processing_time_seconds = Column(Float, nullable=True)
    memory_usage_mb = Column(Float, nullable=True)
    cpu_usage_percentage = Column(Float, nullable=True)
    
    # Worker information
    worker_id = Column(String(100), nullable=True, index=True)
    worker_hostname = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Retry logic
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    next_retry_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timeout
    timeout_seconds = Column(Integer, nullable=True)
    
    # Relaciones
    user = relationship("User")
    document = relationship("Document")
    organization = relationship("Organization")
    steps = relationship("ProcessingStep", back_populates="job", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('ix_jobs_status_priority', 'status', 'priority'),
        Index('ix_jobs_type_status', 'job_type', 'status'),
        Index('ix_jobs_user_created', 'user_id', 'created_at'),
        Index('ix_jobs_worker_status', 'worker_id', 'status'),
    )
    
    @hybrid_property
    def is_running(self):
        """Indica si el job está ejecutándose"""
        return self.status == JobStatus.RUNNING
    
    @hybrid_property
    def is_completed(self):
        """Indica si el job completó (exitoso o con error)"""
        return self.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]
    
    @hybrid_property
    def can_retry(self):
        """Indica si el job puede reintentarse"""
        return (self.status == JobStatus.FAILED and 
                self.retry_count < self.max_retries)
    
    @hybrid_property
    def execution_time(self):
        """Tiempo de ejecución en segundos"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        elif self.started_at:
            return (datetime.utcnow() - self.started_at).total_seconds()
        return None
    
    @hybrid_property
    def is_timeout(self):
        """Indica si el job ha excedido el timeout"""
        if not self.timeout_seconds or not self.started_at:
            return False
        return (datetime.utcnow() - self.started_at).total_seconds() > self.timeout_seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el job a diccionario"""
        return {
            "id": self.id,
            "job_id": self.job_id,
            "job_type": self.job_type.value,
            "status": self.status.value,
            "priority": self.priority,
            "progress_percentage": self.progress_percentage,
            "processing_time_seconds": self.processing_time_seconds,
            "execution_time": self.execution_time,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "is_running": self.is_running,
            "is_completed": self.is_completed,
            "can_retry": self.can_retry,
            "user_id": self.user_id,
            "document_id": self.document_id,
        }
    
    def start(self, worker_id: str = None, worker_hostname: str = None):
        """Marca el job como iniciado"""
        self.status = JobStatus.RUNNING
        self.started_at = datetime.utcnow()
        self.worker_id = worker_id
        self.worker_hostname = worker_hostname
    
    def complete(self, output_data: Dict[str, Any] = None, processing_time: float = None):
        """Marca el job como completado"""
        self.status = JobStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.progress_percentage = 100.0
        if output_data:
            self.output_data = output_data
        if processing_time:
            self.processing_time_seconds = processing_time
    
    def fail(self, error_message: str, error_details: Dict[str, Any] = None):
        """Marca el job como fallido"""
        self.status = JobStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.error_message = error_message
        if error_details:
            self.error_details = error_details
    
    def cancel(self):
        """Cancela el job"""
        self.status = JobStatus.CANCELLED
        self.completed_at = datetime.utcnow()
    
    def schedule_retry(self, delay_seconds: int = 60):
        """Programa un reintento"""
        if self.can_retry:
            self.status = JobStatus.RETRY
            self.retry_count += 1
            self.next_retry_at = datetime.utcnow() + timedelta(seconds=delay_seconds)
    
    def update_progress(self, percentage: float, message: str = None):
        """Actualiza el progreso del job"""
        self.progress_percentage = min(max(percentage, 0.0), 100.0)
        if message:
            # Agregar step de progreso
            step = ProcessingStep(
                job_id=self.id,
                step_name="progress_update",
                status=StepStatus.COMPLETED,
                message=message,
                progress_percentage=self.progress_percentage
            )
            self.steps.append(step)


class StepStatus(enum.Enum):
    """Estados de los pasos de procesamiento"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ProcessingStep(Base):
    """Pasos individuales dentro de un job de procesamiento"""
    __tablename__ = "processing_steps"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey('processing_jobs.id'), nullable=False, index=True)
    
    # Información del paso
    step_name = Column(String(100), nullable=False, index=True)
    step_order = Column(Integer, nullable=False)
    status = Column(SQLEnum(StepStatus), default=StepStatus.PENDING, index=True)
    
    # Detalles del paso
    message = Column(Text, nullable=True)
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Métricas
    progress_percentage = Column(Float, default=0.0, nullable=False)
    processing_time_seconds = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relaciones
    job = relationship("ProcessingJob", back_populates="steps")
    
    __table_args__ = (
        Index('ix_steps_job_order', 'job_id', 'step_order'),
        Index('ix_steps_name_status', 'step_name', 'status'),
    )
    
    def start(self):
        """Inicia el paso"""
        self.status = StepStatus.RUNNING
        self.started_at = datetime.utcnow()
    
    def complete(self, output_data: Dict[str, Any] = None, message: str = None):
        """Completa el paso"""
        self.status = StepStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.progress_percentage = 100.0
        if output_data:
            self.output_data = output_data
        if message:
            self.message = message
    
    def fail(self, error_message: str):
        """Falla el paso"""
        self.status = StepStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.error_message = error_message


class ProcessingQueue(Base):
    """Cola de procesamiento para gestión de trabajos"""
    __tablename__ = "processing_queues"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Configuración de la cola
    max_concurrent_jobs = Column(Integer, default=5, nullable=False)
    priority_weight = Column(Float, default=1.0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Estadísticas
    total_jobs_processed = Column(Integer, default=0, nullable=False)
    current_running_jobs = Column(Integer, default=0, nullable=False)
    average_processing_time = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def can_accept_job(self) -> bool:
        """Verifica si la cola puede aceptar un nuevo job"""
        return (self.is_active and 
                self.current_running_jobs < self.max_concurrent_jobs)


class ProcessingWorker(Base):
    """Workers que procesan los jobs"""
    __tablename__ = "processing_workers"
    
    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(String(100), unique=True, nullable=False, index=True)
    hostname = Column(String(255), nullable=False)
    
    # Estado del worker
    is_active = Column(Boolean, default=True, nullable=False)
    is_busy = Column(Boolean, default=False, nullable=False)
    current_job_id = Column(String(36), nullable=True, index=True)
    
    # Capacidades
    supported_job_types = Column(JSON, nullable=True)  # Lista de tipos que puede procesar
    max_concurrent_jobs = Column(Integer, default=1, nullable=False)
    current_job_count = Column(Integer, default=0, nullable=False)
    
    # Información del sistema
    cpu_cores = Column(Integer, nullable=True)
    memory_mb = Column(Integer, nullable=True)
    disk_space_mb = Column(Integer, nullable=True)
    
    # Estadísticas
    total_jobs_processed = Column(Integer, default=0, nullable=False)
    total_processing_time = Column(Float, default=0.0, nullable=False)
    average_job_time = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_heartbeat = Column(DateTime(timezone=True), server_default=func.now())
    last_job_completed = Column(DateTime(timezone=True), nullable=True)
    
    __table_args__ = (
        Index('ix_workers_active_busy', 'is_active', 'is_busy'),
        Index('ix_workers_heartbeat', 'last_heartbeat'),
    )
    
    @hybrid_property
    def is_online(self):
        """Indica si el worker está online (heartbeat reciente)"""
        if not self.last_heartbeat:
            return False
        return (datetime.utcnow() - self.last_heartbeat).total_seconds() < 300  # 5 minutos
    
    @hybrid_property
    def can_accept_job(self):
        """Indica si el worker puede aceptar un nuevo job"""
        return (self.is_active and 
                self.is_online and 
                not self.is_busy and 
                self.current_job_count < self.max_concurrent_jobs)
    
    def heartbeat(self):
        """Actualiza el heartbeat del worker"""
        self.last_heartbeat = datetime.utcnow()
    
    def assign_job(self, job_id: str):
        """Asigna un job al worker"""
        self.current_job_id = job_id
        self.current_job_count += 1
        self.is_busy = self.current_job_count >= self.max_concurrent_jobs
    
    def complete_job(self, processing_time: float = None):
        """Completa un job en el worker"""
        self.current_job_id = None
        self.current_job_count = max(0, self.current_job_count - 1)
        self.is_busy = self.current_job_count >= self.max_concurrent_jobs
        self.total_jobs_processed += 1
        self.last_job_completed = datetime.utcnow()
        
        if processing_time:
            self.total_processing_time += processing_time
            self.average_job_time = self.total_processing_time / self.total_jobs_processed


class ProcessingMetrics(Base):
    """Métricas de procesamiento para monitoring"""
    __tablename__ = "processing_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Identificadores
    metric_name = Column(String(100), nullable=False, index=True)
    metric_type = Column(String(50), nullable=False)  # counter, gauge, histogram
    
    # Valores
    value = Column(Float, nullable=False)
    tags = Column(JSON, nullable=True)  # Tags adicionales para filtrado
    
    # Timestamps
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    __table_args__ = (
        Index('ix_metrics_name_timestamp', 'metric_name', 'timestamp'),
    )


















