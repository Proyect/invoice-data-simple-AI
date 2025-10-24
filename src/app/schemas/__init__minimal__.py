"""
Schemas Pydantic - Versión Mínima
Solo incluye los schemas que realmente existen y funcionan
"""

# Importar schemas legacy (que existen)
from .document import (
    DocumentBase,
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    DocumentListResponse,
    ExtractedDataResponse,
    ProcessingJobResponse,
    QueueStatsResponse,
    DocumentStatsResponse,
    SearchResultResponse,
    BatchUploadResponse,
    AsyncUploadResponse,
    ReprocessResponse,
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
    "DocumentListResponse", "ExtractedDataResponse", "ProcessingJobResponse",
    "QueueStatsResponse", "DocumentStatsResponse", "SearchResultResponse",
    "BatchUploadResponse", "AsyncUploadResponse", "ReprocessResponse",
    
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
    "UserLoginRequest", "TokenResponse",
    
    # Schemas de compatibilidad
    "DocumentLegacyToEnhanced", "DocumentEnhancedToLegacy",
    "UserLegacyToEnhanced", "UserEnhancedToLegacy",
    "OrganizationLegacyToEnhanced", "OrganizationEnhancedToLegacy",
    "ProcessingJobLegacyToEnhanced", "ProcessingJobEnhancedToLegacy",
]
