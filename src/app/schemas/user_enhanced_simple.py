"""
Schemas Pydantic simplificados para Usuarios Mejorados
Versión básica que funciona con Pydantic v2
"""
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

# Enums
class UserRoleEnum(str, Enum):
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"

class UserStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

# Schemas básicos
class UserEnhancedBase(BaseModel):
    """Schema base para usuarios mejorados"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=255)
    role: UserRoleEnum = Field(default=UserRoleEnum.USER)
    status: UserStatusEnum = Field(default=UserStatusEnum.ACTIVE)

class UserEnhancedCreate(UserEnhancedBase):
    """Schema para crear usuarios mejorados"""
    password: str = Field(..., min_length=8, max_length=128)

class UserEnhancedUpdate(BaseModel):
    """Schema para actualizar usuarios mejorados"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=255)
    role: Optional[UserRoleEnum] = None
    status: Optional[UserStatusEnum] = None

class UserEnhancedResponse(UserEnhancedBase):
    """Schema de respuesta para usuarios mejorados"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Schemas de autenticación
class UserLoginRequest(BaseModel):
    """Schema para login de usuario"""
    username_or_email: str
    password: str

class TokenResponse(BaseModel):
    """Schema de respuesta para tokens"""
    access_token: str
    refresh_token: str

# Schemas de compatibilidad
class UserLegacyToEnhanced(BaseModel):
    """Schema para convertir usuarios legacy a mejorados"""
    legacy_user: Dict[str, Any]
    role: UserRoleEnum = Field(default=UserRoleEnum.USER)

class UserEnhancedToLegacy(BaseModel):
    """Schema para convertir usuarios mejorados a legacy"""
    enhanced_user: UserEnhancedResponse
