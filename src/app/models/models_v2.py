"""
Modelos V2 - Sistema completo mejorado
Este archivo contiene todos los modelos mejorados en un solo lugar para evitar conflictos
"""
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, Float, 
    ForeignKey, Index, func, JSON, Enum as SQLEnum, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR, UUID
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.declarative import declarative_base
import enum
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import uuid

# Base separada para modelos V2
BaseV2 = declarative_base()


# ============================================================================
# ENUMS
# ============================================================================

class DocumentType(enum.Enum):
    FACTURA = "factura"
    RECIBO = "recibo"
    CONTRATO = "contrato"
    FORMULARIO = "formulario"
    CEDULA = "cedula"
    PASAPORTE = "pasaporte"
    LICENCIA = "licencia"
    CERTIFICADO = "certificado"
    OTRO = "otro"


class DocumentStatus(enum.Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    REVIEWING = "reviewing"
    APPROVED = "approved"
    REJECTED = "rejected"


class OCRProvider(enum.Enum):
    TESSERACT = "tesseract"
    GOOGLE_VISION = "google_vision"
    AWS_TEXTRACT = "aws_textract"
    AZURE_OCR = "azure_ocr"
    HYBRID = "hybrid"


class ExtractionMethod(enum.Enum):
    REGEX = "regex"
    SPACY = "spacy"
    LLM = "llm"
    HYBRID = "hybrid"
    MANUAL = "manual"


class UserRole(enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    OPERATOR = "operator"
    REVIEWER = "reviewer"
    USER = "user"
    READONLY = "readonly"


class UserStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"
    BANNED = "banned"


class AuthProvider(enum.Enum):
    LOCAL = "local"
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    GITHUB = "github"
    LDAP = "ldap"


class JobStatus(enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"
    RETRY = "retry"


class JobType(enum.Enum):
    DOCUMENT_OCR = "document_ocr"
    DOCUMENT_EXTRACTION = "document_extraction"
    DOCUMENT_CLASSIFICATION = "document_classification"
    BATCH_PROCESSING = "batch_processing"
    DATA_EXPORT = "data_export"
    CLEANUP = "cleanup"
    BACKUP = "backup"
    REPORT_GENERATION = "report_generation"


class StepStatus(enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


# ============================================================================
# MODELO DE ORGANIZACIÓN
# ============================================================================

class OrganizationV2(BaseV2):
    """Organizaciones para multi-tenancy"""
    __tablename__ = "organizations_v2"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    settings = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    document_limit = Column(Integer, nullable=True)
    storage_limit_mb = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relaciones
    documents = relationship("DocumentV2", back_populates="organization")
    users = relationship("UserV2", back_populates="organization")
    
    def __repr__(self):
        return f"<OrganizationV2(id={self.id}, name='{self.name}')>"


# ============================================================================
# MODELO DE USUARIO V2
# ============================================================================

class UserV2(BaseV2):
    """Usuario con funcionalidades avanzadas"""
    __tablename__ = "users_v2"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    hashed_password = Column(String(255), nullable=True)
    auth_provider = Column(SQLEnum(AuthProvider), default=AuthProvider.LOCAL, nullable=False)
    external_id = Column(String(255), nullable=True, index=True)
    status = Column(SQLEnum(UserStatus), default=UserStatus.PENDING, index=True)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, index=True)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    phone = Column(String(20), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    timezone = Column(String(50), default='UTC', nullable=False)
    language = Column(String(10), default='es', nullable=False)
    organization_id = Column(Integer, ForeignKey('organizations_v2.id'), nullable=True, index=True)
    department = Column(String(100), nullable=True)
    job_title = Column(String(100), nullable=True)
    preferences = Column(JSON, nullable=True)
    permissions = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True, index=True)
    last_activity = Column(DateTime(timezone=True), nullable=True)
    password_changed_at = Column(DateTime(timezone=True), nullable=True)
    email_verified_at = Column(DateTime(timezone=True), nullable=True)
    phone_verified_at = Column(DateTime(timezone=True), nullable=True)
    two_factor_enabled = Column(Boolean, default=False, nullable=False)
    two_factor_secret = Column(String(255), nullable=True)
    documents_processed = Column(Integer, default=0, nullable=False)
    total_processing_time = Column(Float, default=0.0, nullable=False)
    last_document_processed = Column(DateTime(timezone=True), nullable=True)
    daily_document_limit = Column(Integer, nullable=True)
    monthly_document_limit = Column(Integer, nullable=True)
    storage_limit_mb = Column(Integer, nullable=True)
    is_deleted = Column(Boolean, default=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relaciones
    organization = relationship("OrganizationV2", back_populates="users")
    documents = relationship("DocumentV2", foreign_keys="DocumentV2.user_id", back_populates="user")
    reviewed_documents = relationship("DocumentV2", foreign_keys="DocumentV2.reviewed_by")
    
    @hybrid_property
    def is_active(self):
        return self.status == UserStatus.ACTIVE and not self.is_deleted
    
    @hybrid_property
    def full_display_name(self):
        if self.full_name:
            return self.full_name
        elif self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        else:
            return self.username
    
    def has_permission(self, permission: str) -> bool:
        """Verifica si el usuario tiene un permiso específico"""
        if self.is_superuser:
            return True
        
        role_permissions = {
            UserRole.ADMIN: ['*'],
            UserRole.MANAGER: [
                'documents.read', 'documents.create', 'documents.update', 'documents.delete',
                'documents.review', 'users.read', 'reports.read'
            ],
            UserRole.OPERATOR: [
                'documents.read', 'documents.create', 'documents.update', 'documents.process'
            ],
            UserRole.REVIEWER: [
                'documents.read', 'documents.review', 'documents.update'
            ],
            UserRole.USER: [
                'documents.read', 'documents.create'
            ],
            UserRole.READONLY: [
                'documents.read'
            ]
        }
        
        if self.role in role_permissions:
            if '*' in role_permissions[self.role] or permission in role_permissions[self.role]:
                return True
        
        return False
    
    def __repr__(self):
        return f"<UserV2(id={self.id}, username='{self.username}', role='{self.role.value}')>"


# ============================================================================
# MODELO DE DOCUMENTO V2
# ============================================================================

class DocumentV2(BaseV2):
    """Documento con funcionalidades avanzadas"""
    __tablename__ = "documents_v2"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), index=True)
    filename = Column(String(255), nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)
    file_hash = Column(String(64), nullable=True, index=True)
    document_type = Column(SQLEnum(DocumentType), nullable=True, index=True)
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.UPLOADED, index=True)
    priority = Column(Integer, default=5, nullable=False)
    raw_text = Column(Text, nullable=True)
    extracted_data = Column(JSON, nullable=True)
    confidence_score = Column(Float, nullable=True)
    quality_score = Column(Float, nullable=True)
    ocr_provider = Column(SQLEnum(OCRProvider), nullable=True)
    extraction_method = Column(SQLEnum(ExtractionMethod), nullable=True)
    ocr_cost = Column(Float, default=0.0)
    processing_time_seconds = Column(Float, nullable=True)
    language = Column(String(10), default='es', nullable=False)
    page_count = Column(Integer, nullable=True)
    word_count = Column(Integer, nullable=True)
    user_id = Column(Integer, ForeignKey('users_v2.id'), nullable=True, index=True)
    organization_id = Column(Integer, ForeignKey('organizations_v2.id'), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    reviewed_by = Column(Integer, ForeignKey('users_v2.id'), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    review_notes = Column(Text, nullable=True)
    is_deleted = Column(Boolean, default=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relaciones
    user = relationship("UserV2", foreign_keys=[user_id], back_populates="documents")
    reviewer = relationship("UserV2", foreign_keys=[reviewed_by])
    organization = relationship("OrganizationV2", back_populates="documents")
    
    @hybrid_property
    def is_processed(self):
        return self.status in [DocumentStatus.PROCESSED, DocumentStatus.APPROVED]
    
    @hybrid_property
    def file_size_mb(self):
        return self.file_size / (1024 * 1024) if self.file_size else 0
    
    def __repr__(self):
        return f"<DocumentV2(id={self.id}, filename='{self.filename}', status='{self.status.value}')>"


# ============================================================================
# MODELOS DE PROCESAMIENTO
# ============================================================================

class ProcessingJobV2(BaseV2):
    """Jobs de procesamiento asíncrono"""
    __tablename__ = "processing_jobs_v2"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(36), unique=True, nullable=False, index=True)
    job_type = Column(SQLEnum(JobType), nullable=False, index=True)
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING, index=True)
    priority = Column(Integer, default=5, nullable=False)
    user_id = Column(Integer, ForeignKey('users_v2.id'), nullable=True, index=True)
    document_id = Column(Integer, ForeignKey('documents_v2.id'), nullable=True, index=True)
    organization_id = Column(Integer, ForeignKey('organizations_v2.id'), nullable=True, index=True)
    input_data = Column(JSON, nullable=True)
    configuration = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    error_details = Column(JSON, nullable=True)
    progress_percentage = Column(Float, default=0.0, nullable=False)
    processing_time_seconds = Column(Float, nullable=True)
    worker_id = Column(String(100), nullable=True, index=True)
    worker_hostname = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    next_retry_at = Column(DateTime(timezone=True), nullable=True)
    timeout_seconds = Column(Integer, nullable=True)
    
    # Relaciones
    user = relationship("UserV2")
    document = relationship("DocumentV2")
    organization = relationship("OrganizationV2")
    
    @hybrid_property
    def is_running(self):
        return self.status == JobStatus.RUNNING
    
    @hybrid_property
    def is_completed(self):
        return self.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]
    
    def __repr__(self):
        return f"<ProcessingJobV2(id={self.id}, job_id='{self.job_id}', status='{self.status.value}')>"


# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def create_v2_tables(engine):
    """Crear todas las tablas V2"""
    BaseV2.metadata.create_all(bind=engine)


def get_v2_models():
    """Obtener lista de todos los modelos V2"""
    return {
        'OrganizationV2': OrganizationV2,
        'UserV2': UserV2,
        'DocumentV2': DocumentV2,
        'ProcessingJobV2': ProcessingJobV2,
    }


# ============================================================================
# METADATOS
# ============================================================================

MODELS_V2_METADATA = {
    "version": "2.0.0",
    "base_class": "BaseV2",
    "table_suffix": "_v2",
    "models": [
        "OrganizationV2",
        "UserV2", 
        "DocumentV2",
        "ProcessingJobV2"
    ],
    "features": [
        "Sin conflictos con modelos existentes",
        "Tablas separadas con sufijo _v2",
        "Migración gradual posible",
        "Rollback seguro"
    ]
}















