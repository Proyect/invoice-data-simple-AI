"""
Esquemas Pydantic para autenticación
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Esquema base para usuario"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)
    is_active: bool = True
    is_admin: bool = False


class UserCreate(UserBase):
    """Esquema para crear usuario"""
    password: str = Field(..., min_length=8, max_length=128)
    
    @validator('password')
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
    
    @validator('username')
    def validate_username(cls, v):
        """Validar formato de username"""
        if not v.isalnum():
            raise ValueError('El nombre de usuario solo puede contener letras y números')
        return v.lower()


class UserUpdate(BaseModel):
    """Esquema para actualizar usuario"""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    
    @validator('username')
    def validate_username(cls, v):
        """Validar formato de username"""
        if v is not None and not v.isalnum():
            raise ValueError('El nombre de usuario solo puede contener letras y números')
        return v.lower() if v else v


class UserResponse(UserBase):
    """Esquema de respuesta para usuario"""
    id: int
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Esquema para login"""
    username_or_email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    """Esquema de respuesta para tokens"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # segundos


class RefreshTokenRequest(BaseModel):
    """Esquema para solicitar refresh token"""
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    """Esquema para cambiar contraseña"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)
    
    @validator('new_password')
    def validate_new_password(cls, v):
        """Validar fortaleza de nueva contraseña"""
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


class PasswordResetRequest(BaseModel):
    """Esquema para solicitar reset de contraseña"""
    email: EmailStr


class PasswordReset(BaseModel):
    """Esquema para resetear contraseña"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)
    
    @validator('new_password')
    def validate_new_password(cls, v):
        """Validar fortaleza de nueva contraseña"""
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


class MessageResponse(BaseModel):
    """Esquema para respuestas de mensaje"""
    message: str
    success: bool = True
