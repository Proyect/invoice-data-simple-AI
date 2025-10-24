"""
Schemas Pydantic para Usuarios Mejorados
Incluye roles, permisos, autenticación y funcionalidades avanzadas
"""
from pydantic import BaseModel, Field, field_validator, model_validator, EmailStr
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
import re

# ============================================================================
# ENUMS PARA SCHEMAS
# ============================================================================

class UserRoleEnum(str, Enum):
    """Roles de usuario en el sistema"""
    ADMIN = "admin"
    MANAGER = "manager"
    OPERATOR = "operator"
    REVIEWER = "reviewer"
    USER = "user"
    READONLY = "readonly"

class UserStatusEnum(str, Enum):
    """Estados del usuario"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"
    BANNED = "banned"

class AuthProviderEnum(str, Enum):
    """Proveedores de autenticación"""
    LOCAL = "local"
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    GITHUB = "github"
    LDAP = "ldap"

# ============================================================================
# SCHEMAS BASE
# ============================================================================

class UserEnhancedBase(BaseModel):
    """Schema base para usuarios mejorados"""
    email: EmailStr = Field(..., description="Email del usuario")
    username: str = Field(..., min_length=3, max_length=100, description="Nombre de usuario")
    full_name: Optional[str] = Field(None, max_length=255, description="Nombre completo")
    first_name: Optional[str] = Field(None, max_length=100, description="Nombre")
    last_name: Optional[str] = Field(None, max_length=100, description="Apellido")
    phone: Optional[str] = Field(None, max_length=20, description="Teléfono")
    avatar_url: Optional[str] = Field(None, max_length=500, description="URL del avatar")
    timezone: str = Field(default="UTC", max_length=50, description="Zona horaria")
    language: str = Field(default="es", max_length=10, description="Idioma preferido")
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        """Validar formato de username"""
        if not re.match(r'^[a-zA-Z0-9_-]{3,30}$', v):
            raise ValueError('Username debe tener 3-30 caracteres alfanuméricos, guiones o guiones bajos')
        return v.lower()
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        """Validar formato de teléfono"""
        if v is not None:
            # Remover espacios y caracteres especiales para validación
            clean_phone = re.sub(r'[^\d+]', '', v)
            if not re.match(r'^\+?[\d\s\-\(\)]{7,20}$', v):
                raise ValueError('Formato de teléfono inválido')
        return v

# ============================================================================
# SCHEMAS DE CREACIÓN
# ============================================================================

class UserEnhancedCreate(UserEnhancedBase):
    """Schema para crear usuarios mejorados"""
    password: str = Field(..., min_length=8, max_length=128, description="Contraseña")
    role: UserRoleEnum = Field(default=UserRoleEnum.USER, description="Rol del usuario")
    auth_provider: AuthProviderEnum = Field(default=AuthProviderEnum.LOCAL, description="Proveedor de autenticación")
    external_id: Optional[str] = Field(None, max_length=255, description="ID externo (para OAuth)")
    organization_id: Optional[int] = Field(None, description="ID de la organización")
    department: Optional[str] = Field(None, max_length=100, description="Departamento")
    job_title: Optional[str] = Field(None, max_length=100, description="Cargo")
    preferences: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Preferencias del usuario")
    permissions: Optional[List[str]] = Field(default_factory=list, description="Permisos específicos")
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Validar fortaleza de contraseña"""
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        
        if len(v) > 128:
            raise ValueError('La contraseña no puede tener más de 128 caracteres')
        
        # Verificar que tenga al menos una letra minúscula
        if not any(c.islower() for c in v):
            raise ValueError('La contraseña debe contener al menos una letra minúscula')
        
        # Verificar que tenga al menos una letra mayúscula
        if not any(c.isupper() for c in v):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')
        
        # Verificar que tenga al menos un número
        if not any(c.isdigit() for c in v):
            raise ValueError('La contraseña debe contener al menos un número')
        
        # Verificar que tenga al menos un carácter especial
        special_chars = "!@#$%^&*(),.?\":{}|<>"
        if not any(c in special_chars for c in v):
            raise ValueError('La contraseña debe contener al menos un carácter especial')
        
        # Verificar que no contenga espacios
        if ' ' in v:
            raise ValueError('La contraseña no puede contener espacios')
        
        return v
    
    @field_validator('permissions')
    @classmethod
    def validate_permissions(cls, v):
        """Validar permisos"""
        valid_permissions = [
            'documents.read', 'documents.create', 'documents.update', 'documents.delete',
            'documents.process', 'documents.review', 'users.read', 'users.create',
            'users.update', 'users.delete', 'reports.read', 'settings.read',
            'settings.update', 'organizations.read', 'organizations.update'
        ]
        
        for permission in v:
            if permission not in valid_permissions:
                raise ValueError(f'Permiso inválido: {permission}')
        
        return v

class UserEnhancedUpdate(BaseModel):
    """Schema para actualizar usuarios mejorados"""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    avatar_url: Optional[str] = Field(None, max_length=500)
    timezone: Optional[str] = Field(None, max_length=50)
    language: Optional[str] = Field(None, max_length=10)
    role: Optional[UserRoleEnum] = None
    status: Optional[UserStatusEnum] = None
    organization_id: Optional[int] = None
    department: Optional[str] = Field(None, max_length=100)
    job_title: Optional[str] = Field(None, max_length=100)
    preferences: Optional[Dict[str, Any]] = None
    permissions: Optional[List[str]] = None
    is_verified: Optional[bool] = None
    two_factor_enabled: Optional[bool] = None
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        """Validar formato de username"""
        if v is not None:
            if not re.match(r'^[a-zA-Z0-9_-]{3,30}$', v):
                raise ValueError('Username debe tener 3-30 caracteres alfanuméricos, guiones o guiones bajos')
            return v.lower()
        return v
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        """Validar formato de teléfono"""
        if v is not None:
            if not re.match(r'^\+?[\d\s\-\(\)]{7,20}$', v):
                raise ValueError('Formato de teléfono inválido')
        return v
    
    @field_validator('permissions')
    @classmethod
    def validate_permissions(cls, v):
        """Validar permisos"""
        if v is not None:
            valid_permissions = [
                'documents.read', 'documents.create', 'documents.update', 'documents.delete',
                'documents.process', 'documents.review', 'users.read', 'users.create',
                'users.update', 'users.delete', 'reports.read', 'settings.read',
                'settings.update', 'organizations.read', 'organizations.update'
            ]
            
            for permission in v:
                if permission not in valid_permissions:
                    raise ValueError(f'Permiso inválido: {permission}')
        
        return v

# ============================================================================
# SCHEMAS DE RESPUESTA
# ============================================================================

class UserEnhancedResponse(UserEnhancedBase):
    """Schema de respuesta para usuarios mejorados"""
    id: int
    uuid: str
    role: UserRoleEnum
    status: UserStatusEnum
    auth_provider: AuthProviderEnum
    external_id: Optional[str]
    is_superuser: bool
    is_verified: bool
    organization_id: Optional[int]
    department: Optional[str]
    job_title: Optional[str]
    preferences: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]
    last_login: Optional[datetime]
    last_activity: Optional[datetime]
    password_changed_at: Optional[datetime]
    email_verified_at: Optional[datetime]
    phone_verified_at: Optional[datetime]
    two_factor_enabled: bool
    documents_processed: int
    total_processing_time: float
    last_document_processed: Optional[datetime]
    daily_document_limit: Optional[int]
    monthly_document_limit: Optional[int]
    storage_limit_mb: Optional[int]
    is_deleted: bool
    deleted_at: Optional[datetime]
    
    # Campos calculados
    full_display_name: str = Field(description="Nombre completo para mostrar")
    is_active: bool = Field(description="Indica si el usuario está activo")
    can_process_documents: bool = Field(description="Puede procesar documentos")
    can_review_documents: bool = Field(description="Puede revisar documentos")
    needs_password_change: bool = Field(description="Necesita cambiar contraseña")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class UserEnhancedListResponse(BaseModel):
    """Schema para listado de usuarios mejorados"""
    users: List[UserEnhancedResponse]
    total: int = Field(description="Total de usuarios")
    page: int = Field(ge=1, description="Página actual")
    size: int = Field(ge=1, le=100, description="Tamaño de página")
    total_pages: int = Field(description="Total de páginas")
    has_next: bool = Field(description="Tiene página siguiente")
    has_prev: bool = Field(description="Tiene página anterior")

# ============================================================================
# SCHEMAS DE AUTENTICACIÓN
# ============================================================================

class UserLoginRequest(BaseModel):
    """Schema para login de usuario"""
    username_or_email: str = Field(..., min_length=3, description="Username o email")
    password: str = Field(..., min_length=1, description="Contraseña")
    remember_me: bool = Field(default=False, description="Recordar sesión")
    
    @field_validator('username_or_email')
    @classmethod
    def validate_username_or_email(cls, v):
        """Validar que sea email o username válido"""
        v = v.strip()
        if '@' in v:
            # Es un email
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
                raise ValueError('Formato de email inválido')
        else:
            # Es un username
            if not re.match(r'^[a-zA-Z0-9_-]{3,30}$', v):
                raise ValueError('Formato de username inválido')
        return v.lower()

class UserRegisterRequest(UserEnhancedCreate):
    """Schema para registro de usuario"""
    confirm_password: str = Field(..., description="Confirmación de contraseña")
    terms_accepted: bool = Field(..., description="Términos y condiciones aceptados")
    
    @model_validator(mode='after')
    def validate_passwords_match(self):
        """Validar que las contraseñas coincidan"""
        if self.password and self.confirm_password and self.password != self.confirm_password:
            raise ValueError('Las contraseñas no coinciden')
        return self
    
    @field_validator('terms_accepted')
    @classmethod
    def validate_terms_accepted(cls, v):
        """Validar aceptación de términos"""
        if not v:
            raise ValueError('Debes aceptar los términos y condiciones')
        return v

class TokenResponse(BaseModel):
    """Schema de respuesta para tokens"""
    access_token: str = Field(description="Token de acceso")
    refresh_token: str = Field(description="Token de refresco")
    token_type: str = Field(default="bearer", description="Tipo de token")
    expires_in: int = Field(description="Tiempo de expiración en segundos")
    user: UserEnhancedResponse = Field(description="Información del usuario")

class RefreshTokenRequest(BaseModel):
    """Schema para solicitar refresh token"""
    refresh_token: str = Field(..., description="Token de refresco")

class ChangePasswordRequest(BaseModel):
    """Schema para cambiar contraseña"""
    current_password: str = Field(..., description="Contraseña actual")
    new_password: str = Field(..., min_length=8, max_length=128, description="Nueva contraseña")
    confirm_password: str = Field(..., description="Confirmación de nueva contraseña")
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v):
        """Validar fortaleza de nueva contraseña"""
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        
        if not any(c.islower() for c in v):
            raise ValueError('La contraseña debe contener al menos una letra minúscula')
        
        if not any(c.isupper() for c in v):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')
        
        if not any(c.isdigit() for c in v):
            raise ValueError('La contraseña debe contener al menos un número')
        
        special_chars = "!@#$%^&*(),.?\":{}|<>"
        if not any(c in special_chars for c in v):
            raise ValueError('La contraseña debe contener al menos un carácter especial')
        
        if ' ' in v:
            raise ValueError('La contraseña no puede contener espacios')
        
        return v
    
    @model_validator(mode='after')
    def validate_passwords_match(self):
        """Validar que las contraseñas coincidan"""
        if self.new_password and self.confirm_password and self.new_password != self.confirm_password:
            raise ValueError('Las contraseñas no coinciden')
        return self

class PasswordResetRequest(BaseModel):
    """Schema para solicitar reset de contraseña"""
    email: EmailStr = Field(..., description="Email del usuario")

class PasswordReset(BaseModel):
    """Schema para resetear contraseña"""
    token: str = Field(..., description="Token de reset")
    new_password: str = Field(..., min_length=8, max_length=128, description="Nueva contraseña")
    confirm_password: str = Field(..., description="Confirmación de contraseña")
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v):
        """Validar fortaleza de nueva contraseña"""
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        
        if not any(c.islower() for c in v):
            raise ValueError('La contraseña debe contener al menos una letra minúscula')
        
        if not any(c.isupper() for c in v):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')
        
        if not any(c.isdigit() for c in v):
            raise ValueError('La contraseña debe contener al menos un número')
        
        special_chars = "!@#$%^&*(),.?\":{}|<>"
        if not any(c in special_chars for c in v):
            raise ValueError('La contraseña debe contener al menos un carácter especial')
        
        if ' ' in v:
            raise ValueError('La contraseña no puede contener espacios')
        
        return v
    
    @model_validator(mode='after')
    def validate_passwords_match(self):
        """Validar que las contraseñas coincidan"""
        if self.new_password and self.confirm_password and self.new_password != self.confirm_password:
            raise ValueError('Las contraseñas no coinciden')
        return self

# ============================================================================
# SCHEMAS ESPECIALIZADOS
# ============================================================================

class UserSearchRequest(BaseModel):
    """Schema para búsqueda de usuarios"""
    query: Optional[str] = Field(None, max_length=500, description="Texto de búsqueda")
    role: Optional[UserRoleEnum] = None
    status: Optional[UserStatusEnum] = None
    organization_id: Optional[int] = None
    is_verified: Optional[bool] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)
    sort_by: str = Field(default="created_at", pattern="^(created_at|updated_at|username|email|last_login)$")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")
    
    @field_validator('date_to')
    @classmethod
    def validate_date_range(cls, v, values):
        """Validar rango de fechas"""
        if v is not None and 'date_from' in values and values['date_from'] is not None:
            if v < values['date_from']:
                raise ValueError("date_to debe ser mayor o igual a date_from")
        return v

class UserStatsResponse(BaseModel):
    """Schema para estadísticas de usuarios"""
    total_users: int
    by_role: Dict[str, int]
    by_status: Dict[str, int]
    by_organization: Dict[str, int]
    active_users_last_30_days: int
    new_users_last_30_days: int
    users_with_2fa: int

class UserPermissionRequest(BaseModel):
    """Schema para gestionar permisos de usuario"""
    user_id: int
    permissions: List[str] = Field(..., description="Lista de permisos")
    
    @field_validator('permissions')
    @classmethod
    def validate_permissions(cls, v):
        """Validar permisos"""
        valid_permissions = [
            'documents.read', 'documents.create', 'documents.update', 'documents.delete',
            'documents.process', 'documents.review', 'users.read', 'users.create',
            'users.update', 'users.delete', 'reports.read', 'settings.read',
            'settings.update', 'organizations.read', 'organizations.update'
        ]
        
        for permission in v:
            if permission not in valid_permissions:
                raise ValueError(f'Permiso inválido: {permission}')
        
        return v

class UserSessionResponse(BaseModel):
    """Schema para sesiones de usuario"""
    id: int
    session_token: str
    ip_address: Optional[str]
    user_agent: Optional[str]
    device_info: Optional[Dict[str, Any]]
    created_at: datetime
    last_activity: datetime
    expires_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

# ============================================================================
# SCHEMAS DE COMPATIBILIDAD
# ============================================================================

class UserLegacyToEnhanced(BaseModel):
    """Schema para convertir usuarios legacy a mejorados"""
    legacy_user: Dict[str, Any]
    organization_id: Optional[int] = None
    role: UserRoleEnum = Field(default=UserRoleEnum.USER)
    
    @model_validator(mode='after')
    def validate_legacy_user(self):
        """Validar que el usuario legacy tenga campos mínimos"""
        if not self.legacy_user:
            raise ValueError("legacy_user es requerido")
        
        required_fields = ['email', 'username']
        for field in required_fields:
            if field not in self.legacy_user or not self.legacy_user[field]:
                raise ValueError(f"Campo '{field}' es requerido en legacy_user")
        
        return self

class UserEnhancedToLegacy(BaseModel):
    """Schema para convertir usuarios mejorados a legacy"""
    enhanced_user: UserEnhancedResponse
    include_sensitive: bool = Field(default=False)
    
    def to_legacy_dict(self) -> Dict[str, Any]:
        """Convierte a formato legacy"""
        user = self.enhanced_user
        
        legacy_data = {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_admin": user.role == UserRoleEnum.ADMIN or user.is_superuser,
            "is_verified": user.is_verified,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "last_login": user.last_login,
        }
        
        if self.include_sensitive:
            legacy_data.update({
                "preferences": user.preferences,
                "two_factor_enabled": user.two_factor_enabled,
                "needs_password_change": user.needs_password_change,
            })
        
        return legacy_data

class MessageResponse(BaseModel):
    """Schema para respuestas de mensaje"""
    message: str = Field(..., description="Mensaje de respuesta")
    success: bool = Field(default=True, description="Indica si la operación fue exitosa")
    data: Optional[Dict[str, Any]] = Field(None, description="Datos adicionales")