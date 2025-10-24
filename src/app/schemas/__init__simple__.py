"""
Schemas Pydantic - Versión Simplificada
Solo incluye los schemas básicos que funcionan con Pydantic v2
"""

# Importar schemas legacy (que funcionan)
from .document import (
    DocumentBase,
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    DocumentListResponse,
    DocumentSearchRequest,
    DocumentStatsResponse,
    DocumentBatchRequest,
    DocumentBatchResponse,
    DocumentExportRequest,
    DocumentExportResponse,
    DocumentProcessingRequest,
    DocumentProcessingResponse,
    DocumentReviewRequest,
    DocumentReviewResponse,
)

from .auth import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse,
    UserLogin,
    UserLoginResponse,
    UserRegister,
    UserRegisterResponse,
    Token,
    TokenData,
    PasswordReset,
    PasswordResetRequest,
    PasswordChange,
    PasswordChangeRequest,
)

# Importar schemas mejorados simplificados
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
    DocumentProcessingRequest as DocumentEnhancedProcessingRequest,
    DocumentReviewRequest as DocumentEnhancedReviewRequest,
    DocumentSearchRequest as DocumentEnhancedSearchRequest,
    DocumentStatsResponse as DocumentEnhancedStatsResponse,
    DocumentBatchRequest as DocumentEnhancedBatchRequest,
    DocumentExportRequest as DocumentEnhancedExportRequest,
    
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
)

from .organization_simple import (
    # Enums
    OrganizationPlanEnum,
    OrganizationStatusEnum,
    
    # Schemas principales
    OrganizationBase,
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
    
    # Schemas de compatibilidad
    OrganizationLegacyToEnhanced,
    OrganizationEnhancedToLegacy,
)

from .processing_simple import (
    # Enums
    JobStatusEnum,
    JobTypeEnum,
    
    # Schemas principales
    ProcessingJobBase,
    ProcessingJobCreate,
    ProcessingJobUpdate,
    ProcessingJobResponse,
    
    # Schemas de compatibilidad
    ProcessingJobLegacyToEnhanced,
    ProcessingJobEnhancedToLegacy,
)

# Lista de todos los schemas exportados
__all__ = [
    # Schemas legacy
    "DocumentBase", "DocumentCreate", "DocumentUpdate", "DocumentResponse",
    "DocumentListResponse", "DocumentSearchRequest", "DocumentStatsResponse",
    "DocumentBatchRequest", "DocumentBatchResponse", "DocumentExportRequest",
    "DocumentExportResponse", "DocumentProcessingRequest", "DocumentProcessingResponse",
    "DocumentReviewRequest", "DocumentReviewResponse",
    
    "UserBase", "UserCreate", "UserUpdate", "UserResponse", "UserListResponse",
    "UserLogin", "UserLoginResponse", "UserRegister", "UserRegisterResponse",
    "Token", "TokenData", "PasswordReset", "PasswordResetRequest",
    "PasswordChange", "PasswordChangeRequest",
    
    # Enums mejorados
    "DocumentTypeEnum", "DocumentStatusEnum", "OCRProviderEnum", "ExtractionMethodEnum",
    "UserRoleEnum", "UserStatusEnum",
    "OrganizationPlanEnum", "OrganizationStatusEnum",
    "JobStatusEnum", "JobTypeEnum",
    
    # Schemas mejorados principales
    "DocumentEnhancedBase", "DocumentEnhancedCreate", "DocumentEnhancedUpdate",
    "DocumentEnhancedResponse", "DocumentEnhancedListResponse",
    "UserEnhancedBase", "UserEnhancedCreate", "UserEnhancedUpdate", "UserEnhancedResponse",
    "OrganizationBase", "OrganizationCreate", "OrganizationUpdate", "OrganizationResponse",
    "ProcessingJobBase", "ProcessingJobCreate", "ProcessingJobUpdate", "ProcessingJobResponse",
    
    # Schemas especializados
    "DocumentEnhancedProcessingRequest", "DocumentEnhancedReviewRequest",
    "DocumentEnhancedSearchRequest", "DocumentEnhancedStatsResponse",
    "DocumentEnhancedBatchRequest", "DocumentEnhancedExportRequest",
    "UserLoginRequest", "TokenResponse",
    
    # Schemas de compatibilidad
    "DocumentLegacyToEnhanced", "DocumentEnhancedToLegacy",
    "UserLegacyToEnhanced", "UserEnhancedToLegacy",
    "OrganizationLegacyToEnhanced", "OrganizationEnhancedToLegacy",
    "ProcessingJobLegacyToEnhanced", "ProcessingJobEnhancedToLegacy",
]
