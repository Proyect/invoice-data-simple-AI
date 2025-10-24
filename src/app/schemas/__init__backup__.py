"""
Schemas Pydantic para validación y serialización de la API

Este módulo contiene todos los schemas de Pydantic para:
- Validación de entrada de datos
- Serialización de respuestas
- Documentación automática de la API
"""

# Importar schemas básicos (compatibilidad)
from .document import DocumentResponse as DocumentBasicResponse, DocumentListResponse as DocumentBasicListResponse
from .auth import UserResponse as UserBasicResponse

# Importar schemas mejorados
from .document_enhanced import (
    # Enums
    DocumentTypeEnum,
    DocumentStatusEnum,
    OCRProviderEnum,
    ExtractionMethodEnum,
    
    # Schemas principales
    DocumentEnhancedBase,
    DocumentEnhancedCreate,
    DocumentEnhancedUpdate,
    DocumentEnhancedResponse,
    DocumentEnhancedListResponse,
    
    # Schemas especializados
    DocumentProcessingRequest,
    DocumentReviewRequest,
    DocumentSearchRequest,
    DocumentStatsResponse,
    DocumentBatchOperationRequest,
    DocumentExportRequest,
    
    # Schemas de compatibilidad
    DocumentLegacyToEnhanced,
    DocumentEnhancedToLegacy,
)

from .user_enhanced_simple import (
    # Enums
    UserRoleEnum,
    UserStatusEnum,
    
    # Schemas principales
    UserEnhancedBase,
    UserEnhancedCreate,
    UserEnhancedUpdate,
    UserEnhancedResponse,
    
    # Schemas de autenticación
    UserLoginRequest,
    TokenResponse,
    
    # Schemas de compatibilidad
    UserLegacyToEnhanced,
    UserEnhancedToLegacy,
    MessageResponse,
)

from .organization import (
    # Enums
    OrganizationStatusEnum,
    OrganizationPlanEnum,
    OrganizationFeatureEnum,
    
    # Schemas principales
    OrganizationBase,
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
    OrganizationListResponse,
    
    # Schemas especializados
    OrganizationMemberRequest,
    OrganizationMemberResponse,
    OrganizationStatsResponse,
    OrganizationSearchRequest,
    OrganizationSettingsUpdate,
    OrganizationPlanUpgrade,
    OrganizationBillingInfo,
    
    # Schemas de invitaciones
    OrganizationInviteRequest,
    OrganizationInviteResponse,
    
    # Schemas de actividad
    OrganizationActivityLog,
    
    # Schemas de compatibilidad
    OrganizationLegacyToEnhanced,
    OrganizationEnhancedToLegacy,
)

from .processing import (
    # Enums
    JobStatusEnum,
    JobTypeEnum,
    StepStatusEnum,
    
    # Schemas de jobs
    ProcessingJobBase,
    ProcessingJobCreate,
    ProcessingJobUpdate,
    ProcessingJobResponse,
    ProcessingJobListResponse,
    
    # Schemas de steps
    ProcessingStepCreate,
    ProcessingStepUpdate,
    ProcessingStepResponse,
    
    # Schemas especializados
    ProcessingJobSearchRequest,
    ProcessingJobStatsResponse,
    ProcessingJobCancelRequest,
    ProcessingJobRetryRequest,
    ProcessingJobBatchRequest,
    
    # Schemas de configuración
    OCRJobConfiguration,
    ExtractionJobConfiguration,
    BatchProcessingConfiguration,
    
    # Schemas de monitoreo
    ProcessingQueueStatus,
    WorkerStatus,
    ProcessingMetrics,
    
    # Schemas de notificaciones
    ProcessingNotification,
)

# Lista de todos los schemas para referencia
__all__ = [
    # Schemas básicos (compatibilidad)
    "DocumentBasicResponse",
    "DocumentBasicListResponse", 
    "UserBasicResponse",
    
    # Enums de documentos
    "DocumentTypeEnum",
    "DocumentStatusEnum",
    "OCRProviderEnum", 
    "ExtractionMethodEnum",
    
    # Schemas principales de documentos
    "DocumentEnhancedBase",
    "DocumentEnhancedCreate",
    "DocumentEnhancedUpdate", 
    "DocumentEnhancedResponse",
    "DocumentEnhancedListResponse",
    
    # Schemas especializados de documentos
    "DocumentProcessingRequest",
    "DocumentReviewRequest",
    "DocumentSearchRequest",
    "DocumentStatsResponse",
    "DocumentBatchOperationRequest",
    "DocumentExportRequest",
    
    # Schemas de compatibilidad de documentos
    "DocumentLegacyToEnhanced",
    "DocumentEnhancedToLegacy",
    
    # Enums de usuarios
    "UserRoleEnum",
    "UserStatusEnum",
    "AuthProviderEnum",
    
    # Schemas principales de usuarios
    "UserEnhancedBase",
    "UserEnhancedCreate",
    "UserEnhancedUpdate",
    "UserEnhancedResponse",
    "UserEnhancedListResponse",
    
    # Schemas de autenticación
    "UserLoginRequest",
    "UserRegisterRequest",
    "TokenResponse",
    "RefreshTokenRequest",
    "ChangePasswordRequest",
    "PasswordResetRequest",
    "PasswordReset",
    
    # Schemas especializados de usuarios
    "UserSearchRequest",
    "UserStatsResponse",
    "UserPermissionRequest",
    "UserSessionResponse",
    
    # Schemas de compatibilidad de usuarios
    "UserLegacyToEnhanced",
    "UserEnhancedToLegacy",
    "MessageResponse",
    
    # Enums de organizaciones
    "OrganizationStatusEnum",
    "OrganizationPlanEnum",
    "OrganizationFeatureEnum",
    
    # Schemas principales de organizaciones
    "OrganizationBase",
    "OrganizationCreate",
    "OrganizationUpdate",
    "OrganizationResponse",
    "OrganizationListResponse",
    
    # Schemas especializados de organizaciones
    "OrganizationMemberRequest",
    "OrganizationMemberResponse",
    "OrganizationStatsResponse",
    "OrganizationSearchRequest",
    "OrganizationSettingsUpdate",
    "OrganizationPlanUpgrade",
    "OrganizationBillingInfo",
    "OrganizationInviteRequest",
    "OrganizationInviteResponse",
    "OrganizationActivityLog",
    
    # Schemas de compatibilidad de organizaciones
    "OrganizationLegacyToEnhanced",
    "OrganizationEnhancedToLegacy",
    
    # Enums de procesamiento
    "JobStatusEnum",
    "JobTypeEnum", 
    "StepStatusEnum",
    
    # Schemas principales de procesamiento
    "ProcessingJobBase",
    "ProcessingJobCreate",
    "ProcessingJobUpdate",
    "ProcessingJobResponse",
    "ProcessingJobListResponse",
    
    # Schemas de steps de procesamiento
    "ProcessingStepCreate", 
    "ProcessingStepUpdate",
    "ProcessingStepResponse",
    
    # Schemas especializados de procesamiento
    "ProcessingJobSearchRequest",
    "ProcessingJobStatsResponse",
    "ProcessingJobCancelRequest",
    "ProcessingJobRetryRequest",
    "ProcessingJobBatchRequest",
    
    # Schemas de configuración de procesamiento
    "OCRJobConfiguration",
    "ExtractionJobConfiguration",
    "BatchProcessingConfiguration",
    
    # Schemas de monitoreo de procesamiento
    "ProcessingQueueStatus",
    "WorkerStatus",
    "ProcessingMetrics",
    "ProcessingNotification",
]

# Metadatos para documentación
SCHEMAS_METADATA = {
    "version": "2.0.0",
    "description": "Schemas Pydantic completos para el sistema de extracción de documentos",
    "categories": {
        "documents": "Schemas para gestión de documentos y extracción",
        "users": "Schemas para usuarios, autenticación y permisos",
        "organizations": "Schemas para multi-tenancy y organizaciones", 
        "processing": "Schemas para procesamiento asíncrono y workers",
        "common": "Schemas comunes y utilidades"
    },
    "features": [
        "Validación completa de entrada de datos",
        "Serialización optimizada de respuestas",
        "Documentación automática de API",
        "Soporte para paginación y filtros",
        "Schemas para operaciones batch",
        "Métricas y estadísticas detalladas",
        "Configuraciones flexibles",
        "Compatibilidad con modelos existentes"
    ]
}