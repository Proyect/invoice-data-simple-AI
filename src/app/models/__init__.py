"""
Modelos de la aplicación - Sistema de extracción de documentos V2

IMPORTANTE: Este módulo usa los modelos V2 que evitan conflictos de nombres
Para compatibilidad con código existente, se mantienen alias
"""

# Importar modelos V2 (sin conflictos)
from .models_v2 import (
    # Modelos principales
    DocumentV2 as Document,
    UserV2 as User, 
    OrganizationV2 as Organization,
    ProcessingJobV2 as ProcessingJob,
    
    # Enums
    DocumentType,
    DocumentStatus,
    OCRProvider,
    ExtractionMethod,
    UserRole,
    UserStatus,
    AuthProvider,
    JobStatus,
    JobType,
    StepStatus,
    
    # Base y utilidades
    BaseV2 as Base,
    create_v2_tables,
    get_v2_models,
    MODELS_V2_METADATA
)

# Alias para compatibilidad con código existente
DocumentBasic = Document  # Para que el código actual siga funcionando
UserBasic = User         # Para que el código actual siga funcionando

# Lista de todos los modelos para migraciones
__all__ = [
    # Modelos básicos (compatibilidad)
    "DocumentBasic",
    "UserBasic",
    
    # Modelos principales mejorados
    "Document",
    "User",
    "Organization",
    
    # Enums de documentos
    "DocumentType",
    "DocumentStatus", 
    "OCRProvider",
    "ExtractionMethod",
    
    # Modelos relacionados con documentos
    "DocumentVersion",
    "DocumentExtraction",
    "DocumentTag",
    
    # Enums de usuarios
    "UserRole",
    "UserStatus",
    "AuthProvider",
    
    # Modelos relacionados con usuarios
    "UserSession",
    "ApiKey",
    "AuditLog",
    
    # Modelos de procesamiento
    "ProcessingJob",
    "ProcessingStep",
    "ProcessingQueue",
    "ProcessingWorker",
    "ProcessingMetrics",
    
    # Enums de procesamiento
    "JobStatus",
    "JobType",
    "StepStatus",
]

# Metadatos para migraciones automáticas
MODELS_METADATA = {
    "version": "2.0.0",
    "description": "Sistema completo de extracción de documentos con funcionalidades avanzadas",
    "models": {
        "core": ["Document", "User", "Organization"],
        "processing": ["ProcessingJob", "ProcessingStep", "ProcessingQueue", "ProcessingWorker"],
        "audit": ["AuditLog", "UserSession", "ApiKey"],
        "versioning": ["DocumentVersion", "DocumentExtraction", "DocumentTag"],
        "metrics": ["ProcessingMetrics"]
    },
    "features": [
        "Multi-tenancy con organizaciones",
        "Sistema de roles y permisos granular",
        "Procesamiento asíncrono con workers",
        "Versionado de documentos",
        "Auditoría completa de acciones",
        "Métricas y monitoring",
        "API Keys para acceso programático",
        "Soft delete y recuperación",
        "Búsqueda full-text (PostgreSQL)",
        "Detección de duplicados",
        "Sistema de tags flexible"
    ]
}