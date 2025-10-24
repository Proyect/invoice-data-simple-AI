"""
Schemas Pydantic simplificados para Organizaciones
Versión básica que funciona con Pydantic v2
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

# Enums
class OrganizationPlanEnum(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"

class OrganizationStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

# Schemas básicos
class OrganizationBase(BaseModel):
    """Schema base para organizaciones"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    plan: OrganizationPlanEnum = Field(default=OrganizationPlanEnum.FREE)
    status: OrganizationStatusEnum = Field(default=OrganizationStatusEnum.ACTIVE)

class OrganizationCreate(OrganizationBase):
    """Schema para crear organizaciones"""
    pass

class OrganizationUpdate(BaseModel):
    """Schema para actualizar organizaciones"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    plan: Optional[OrganizationPlanEnum] = None
    status: Optional[OrganizationStatusEnum] = None

class OrganizationResponse(OrganizationBase):
    """Schema de respuesta para organizaciones"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Schemas de compatibilidad
class OrganizationLegacyToEnhanced(BaseModel):
    """Schema para convertir organizaciones legacy a mejoradas"""
    legacy_organization: Dict[str, Any]
    plan: OrganizationPlanEnum = Field(default=OrganizationPlanEnum.FREE)

class OrganizationEnhancedToLegacy(BaseModel):
    """Schema para convertir organizaciones mejoradas a legacy"""
    enhanced_organization: OrganizationResponse
