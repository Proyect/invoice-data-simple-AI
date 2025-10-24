"""
Schemas Pydantic para Organizaciones
Soporte para multi-tenancy y gestión de organizaciones
"""
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
import re

# ============================================================================
# ENUMS PARA SCHEMAS
# ============================================================================

class OrganizationStatusEnum(str, Enum):
    """Estados de la organización"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"

class OrganizationPlanEnum(str, Enum):
    """Planes de organización"""
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class OrganizationFeatureEnum(str, Enum):
    """Características disponibles para organizaciones"""
    DOCUMENT_PROCESSING = "document_processing"
    BULK_UPLOAD = "bulk_upload"
    API_ACCESS = "api_access"
    ADVANCED_ANALYTICS = "advanced_analytics"
    CUSTOM_BRANDING = "custom_branding"
    PRIORITY_SUPPORT = "priority_support"
    SSO = "sso"
    AUDIT_LOGS = "audit_logs"

# ============================================================================
# SCHEMAS BASE
# ============================================================================

class OrganizationBase(BaseModel):
    """Schema base para organizaciones"""
    name: str = Field(..., min_length=1, max_length=255, description="Nombre de la organización")
    slug: str = Field(..., min_length=3, max_length=100, description="Slug único de la organización")
    description: Optional[str] = Field(None, max_length=1000, description="Descripción de la organización")
    
    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v):
        """Validar formato del slug"""
        if not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('El slug solo puede contener letras minúsculas, números y guiones')
        
        if v.startswith('-') or v.endswith('-'):
            raise ValueError('El slug no puede empezar o terminar con guión')
        
        return v.lower()

# ============================================================================
# SCHEMAS DE CREACIÓN
# ============================================================================

class OrganizationCreate(OrganizationBase):
    """Schema para crear organizaciones"""
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Configuraciones específicas")
    plan: OrganizationPlanEnum = Field(default=OrganizationPlanEnum.FREE, description="Plan de la organización")
    features: List[OrganizationFeatureEnum] = Field(default_factory=list, description="Características habilitadas")
    document_limit: Optional[int] = Field(None, ge=0, description="Límite de documentos")
    storage_limit_mb: Optional[int] = Field(None, ge=0, description="Límite de almacenamiento en MB")
    owner_id: Optional[int] = Field(None, description="ID del usuario propietario")
    
    @field_validator('features')
    @classmethod
    def validate_features(cls, v):
        """Validar características según el plan"""
        # Definir características por plan
        plan_features = {
            OrganizationPlanEnum.FREE: [
                OrganizationFeatureEnum.DOCUMENT_PROCESSING
            ],
            OrganizationPlanEnum.BASIC: [
                OrganizationFeatureEnum.DOCUMENT_PROCESSING,
                OrganizationFeatureEnum.BULK_UPLOAD,
                OrganizationFeatureEnum.API_ACCESS
            ],
            OrganizationPlanEnum.PROFESSIONAL: [
                OrganizationFeatureEnum.DOCUMENT_PROCESSING,
                OrganizationFeatureEnum.BULK_UPLOAD,
                OrganizationFeatureEnum.API_ACCESS,
                OrganizationFeatureEnum.ADVANCED_ANALYTICS,
                OrganizationFeatureEnum.CUSTOM_BRANDING
            ],
            OrganizationPlanEnum.ENTERPRISE: [
                OrganizationFeatureEnum.DOCUMENT_PROCESSING,
                OrganizationFeatureEnum.BULK_UPLOAD,
                OrganizationFeatureEnum.API_ACCESS,
                OrganizationFeatureEnum.ADVANCED_ANALYTICS,
                OrganizationFeatureEnum.CUSTOM_BRANDING,
                OrganizationFeatureEnum.PRIORITY_SUPPORT,
                OrganizationFeatureEnum.SSO,
                OrganizationFeatureEnum.AUDIT_LOGS
            ]
        }
        
        # Esta validación se hará en el servicio, aquí solo validamos formato
        return v
    
    @field_validator('document_limit')
    @classmethod
    def validate_document_limit(cls, v, values):
        """Validar límite de documentos según el plan"""
        if v is not None:
            plan = OrganizationPlanEnum.FREE
            
            # Límites por plan
            plan_limits = {
                OrganizationPlanEnum.FREE: 100,
                OrganizationPlanEnum.BASIC: 1000,
                OrganizationPlanEnum.PROFESSIONAL: 10000,
                OrganizationPlanEnum.ENTERPRISE: None  # Sin límite
            }
            
            if plan != OrganizationPlanEnum.ENTERPRISE and v > plan_limits.get(plan, 100):
                raise ValueError(f'El límite de documentos excede el permitido para el plan {plan.value}')
        
        return v

    @field_validator('storage_limit_mb')
    @classmethod
    def validate_storage_limit(cls, v, values):
        """Validar límite de almacenamiento según el plan"""
        if v is not None:
            plan = OrganizationPlanEnum.FREE
            
            # Límites por plan en MB
            plan_limits = {
                OrganizationPlanEnum.FREE: 1000,  # 1GB
                OrganizationPlanEnum.BASIC: 10000,  # 10GB
                OrganizationPlanEnum.PROFESSIONAL: 100000,  # 100GB
                OrganizationPlanEnum.ENTERPRISE: None  # Sin límite
            }
            
            if plan != OrganizationPlanEnum.ENTERPRISE and v > plan_limits.get(plan, 1000):
                raise ValueError(f'El límite de almacenamiento excede el permitido para el plan {plan.value}')
        
        return v

class OrganizationUpdate(BaseModel):
    """Schema para actualizar organizaciones"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    settings: Optional[Dict[str, Any]] = None
    plan: Optional[OrganizationPlanEnum] = None
    features: Optional[List[OrganizationFeatureEnum]] = None
    document_limit: Optional[int] = Field(None, ge=0)
    storage_limit_mb: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    
    @field_validator('features')
    @classmethod
    def validate_features(cls, v):
        """Validar características"""
        if v is not None:
            # Validación básica de formato
            return v
        return v

# ============================================================================
# SCHEMAS DE RESPUESTA
# ============================================================================

class OrganizationResponse(OrganizationBase):
    """Schema de respuesta para organizaciones"""
    id: int
    settings: Optional[Dict[str, Any]]
    plan: OrganizationPlanEnum
    features: List[OrganizationFeatureEnum]
    is_active: bool
    document_limit: Optional[int]
    storage_limit_mb: Optional[int]
    owner_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Campos calculados
    current_document_count: Optional[int] = Field(None, description="Cantidad actual de documentos")
    current_storage_mb: Optional[float] = Field(None, description="Almacenamiento actual en MB")
    usage_percentage: Optional[float] = Field(None, description="Porcentaje de uso")
    is_at_limit: bool = Field(description="Indica si está cerca del límite")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class OrganizationListResponse(BaseModel):
    """Schema para listado de organizaciones"""
    organizations: List[OrganizationResponse]
    total: int = Field(description="Total de organizaciones")
    page: int = Field(ge=1, description="Página actual")
    size: int = Field(ge=1, le=100, description="Tamaño de página")
    total_pages: int = Field(description="Total de páginas")
    has_next: bool = Field(description="Tiene página siguiente")
    has_prev: bool = Field(description="Tiene página anterior")

# ============================================================================
# SCHEMAS ESPECIALIZADOS
# ============================================================================

class OrganizationMemberRequest(BaseModel):
    """Schema para agregar/quitar miembros de organización"""
    user_id: int = Field(..., description="ID del usuario")
    role: str = Field(default="member", pattern="^(owner|admin|manager|member|viewer)$", description="Rol del usuario")
    
class OrganizationMemberResponse(BaseModel):
    """Schema de respuesta para miembros de organización"""
    id: int
    user_id: int
    organization_id: int
    role: str
    joined_at: datetime
    is_active: bool
    user: Optional[Dict[str, Any]] = Field(None, description="Información del usuario")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class OrganizationStatsResponse(BaseModel):
    """Schema para estadísticas de organización"""
    organization_id: int
    total_users: int
    total_documents: int
    total_storage_mb: float
    documents_by_type: Dict[str, int]
    documents_by_month: Dict[str, int]
    processing_stats: Dict[str, Any]
    usage_stats: Dict[str, Any]

class OrganizationSearchRequest(BaseModel):
    """Schema para búsqueda de organizaciones"""
    query: Optional[str] = Field(None, max_length=500, description="Texto de búsqueda")
    plan: Optional[OrganizationPlanEnum] = None
    is_active: Optional[bool] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    has_feature: Optional[OrganizationFeatureEnum] = None
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)
    sort_by: str = Field(default="created_at", pattern="^(created_at|updated_at|name|plan)$")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")
    
    @field_validator('date_to')
    @classmethod
    def validate_date_range(cls, v, values):
        """Validar rango de fechas"""
        if v is not None and 'date_from' in values and values['date_from'] is not None:
            if v < values['date_from']:
                raise ValueError("date_to debe ser mayor o igual a date_from")
        return v

class OrganizationSettingsUpdate(BaseModel):
    """Schema para actualizar configuraciones de organización"""
    settings: Dict[str, Any] = Field(..., description="Nuevas configuraciones")
    
    @field_validator('settings')
    @classmethod
    def validate_settings(cls, v):
        """Validar configuraciones"""
        # Configuraciones válidas
        valid_settings = {
            'theme', 'logo_url', 'primary_color', 'secondary_color',
            'default_language', 'timezone', 'date_format', 'currency',
            'notifications', 'email_templates', 'api_rate_limit',
            'document_retention_days', 'auto_delete_processed',
            'require_approval', 'default_ocr_provider'
        }
        
        for key in v.keys():
            if key not in valid_settings:
                raise ValueError(f'Configuración inválida: {key}')
        
        return v

class OrganizationPlanUpgrade(BaseModel):
    """Schema para upgrade de plan de organización"""
    new_plan: OrganizationPlanEnum = Field(..., description="Nuevo plan")
    features_to_add: Optional[List[OrganizationFeatureEnum]] = Field(None, description="Características adicionales")
    billing_cycle: str = Field(default="monthly", pattern="^(monthly|yearly)$", description="Ciclo de facturación")
    
    @field_validator('features_to_add')
    @classmethod
    def validate_features_for_plan(cls, v, values):
        """Validar que las características sean compatibles con el plan"""
        if v is not None:
            new_plan = OrganizationPlanEnum.FREE
            if new_plan:
                # Validar que las características estén disponibles para el plan
                plan_features = {
                    OrganizationPlanEnum.FREE: [
                        OrganizationFeatureEnum.DOCUMENT_PROCESSING
                    ],
                    OrganizationPlanEnum.BASIC: [
                        OrganizationFeatureEnum.DOCUMENT_PROCESSING,
                        OrganizationFeatureEnum.BULK_UPLOAD,
                        OrganizationFeatureEnum.API_ACCESS
                    ],
                    OrganizationPlanEnum.PROFESSIONAL: [
                        OrganizationFeatureEnum.DOCUMENT_PROCESSING,
                        OrganizationFeatureEnum.BULK_UPLOAD,
                        OrganizationFeatureEnum.API_ACCESS,
                        OrganizationFeatureEnum.ADVANCED_ANALYTICS,
                        OrganizationFeatureEnum.CUSTOM_BRANDING
                    ],
                    OrganizationPlanEnum.ENTERPRISE: [
                        OrganizationFeatureEnum.DOCUMENT_PROCESSING,
                        OrganizationFeatureEnum.BULK_UPLOAD,
                        OrganizationFeatureEnum.API_ACCESS,
                        OrganizationFeatureEnum.ADVANCED_ANALYTICS,
                        OrganizationFeatureEnum.CUSTOM_BRANDING,
                        OrganizationFeatureEnum.PRIORITY_SUPPORT,
                        OrganizationFeatureEnum.SSO,
                        OrganizationFeatureEnum.AUDIT_LOGS
                    ]
                }
                
                available_features = plan_features.get(new_plan, [])
                for feature in v:
                    if feature not in available_features:
                        raise ValueError(f'La característica {feature.value} no está disponible para el plan {new_plan.value}')
        
        return v

class OrganizationBillingInfo(BaseModel):
    """Schema para información de facturación"""
    organization_id: int
    plan: OrganizationPlanEnum
    billing_cycle: str
    monthly_cost: float
    yearly_cost: float
    features_included: List[OrganizationFeatureEnum]
    usage_this_month: Dict[str, Any]
    next_billing_date: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

# ============================================================================
# SCHEMAS DE COMPATIBILIDAD
# ============================================================================

class OrganizationLegacyToEnhanced(BaseModel):
    """Schema para convertir organizaciones legacy a mejoradas"""
    legacy_organization: Dict[str, Any]
    plan: OrganizationPlanEnum = Field(default=OrganizationPlanEnum.FREE)
    owner_id: Optional[int] = None
    
    @model_validator(mode='after')
    def validate_legacy_organization(self):
        """Validar que la organización legacy tenga campos mínimos"""
        if not self.legacy_organization:
            raise ValueError("legacy_organization es requerido")
        
        required_fields = ['name']
        for field in required_fields:
            if field not in self.legacy_organization or not self.legacy_organization[field]:
                raise ValueError(f"Campo '{field}' es requerido en legacy_organization")
        
        return self

class OrganizationEnhancedToLegacy(BaseModel):
    """Schema para convertir organizaciones mejoradas a legacy"""
    enhanced_organization: OrganizationResponse
    include_stats: bool = Field(default=False)
    
    def to_legacy_dict(self) -> Dict[str, Any]:
        """Convierte a formato legacy"""
        org = self.enhanced_organization
        
        legacy_data = {
            "id": org.id,
            "name": org.name,
            "slug": org.slug,
            "description": org.description,
            "is_active": org.is_active,
            "created_at": org.created_at,
            "updated_at": org.updated_at,
        }
        
        if self.include_stats:
            legacy_data.update({
                "plan": org.plan.value,
                "features": [f.value for f in org.features],
                "document_limit": org.document_limit,
                "storage_limit_mb": org.storage_limit_mb,
                "current_document_count": org.current_document_count,
                "current_storage_mb": org.current_storage_mb,
            })
        
        return legacy_data

# ============================================================================
# SCHEMAS DE UTILIDAD
# ============================================================================

class OrganizationInviteRequest(BaseModel):
    """Schema para invitar usuarios a organización"""
    email: str = Field(..., description="Email del usuario a invitar")
    role: str = Field(default="member", pattern="^(admin|manager|member|viewer)$", description="Rol a asignar")
    message: Optional[str] = Field(None, max_length=500, description="Mensaje personalizado")

class OrganizationInviteResponse(BaseModel):
    """Schema de respuesta para invitaciones"""
    id: int
    organization_id: int
    email: str
    role: str
    invited_by: int
    token: str
    expires_at: datetime
    accepted_at: Optional[datetime]
    is_expired: bool
    is_accepted: bool
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class OrganizationActivityLog(BaseModel):
    """Schema para log de actividad de organización"""
    id: int
    organization_id: int
    user_id: Optional[int]
    action: str
    resource_type: str
    resource_id: Optional[str]
    details: Optional[Dict[str, Any]]
    ip_address: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }