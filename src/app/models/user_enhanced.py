"""
Modelo de Usuario Mejorado con roles, permisos y funcionalidades avanzadas
"""
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, Float,
    ForeignKey, Index, func, JSON, Enum as SQLEnum, UniqueConstraint
)
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.hybrid import hybrid_property
from ..core.database import Base
import enum
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import uuid


class UserRole(enum.Enum):
    """Roles de usuario en el sistema"""
    ADMIN = "admin"                 # Administrador del sistema
    MANAGER = "manager"             # Gerente de organización
    OPERATOR = "operator"           # Operador que procesa documentos
    REVIEWER = "reviewer"           # Revisor de documentos
    USER = "user"                   # Usuario básico
    READONLY = "readonly"           # Solo lectura


class UserStatus(enum.Enum):
    """Estados del usuario"""
    ACTIVE = "active"               # Activo
    INACTIVE = "inactive"           # Inactivo
    SUSPENDED = "suspended"         # Suspendido
    PENDING = "pending"             # Pendiente de activación
    BANNED = "banned"               # Baneado


class AuthProvider(enum.Enum):
    """Proveedores de autenticación"""
    LOCAL = "local"                 # Autenticación local
    GOOGLE = "google"               # Google OAuth
    MICROSOFT = "microsoft"         # Microsoft OAuth
    GITHUB = "github"               # GitHub OAuth
    LDAP = "ldap"                   # LDAP/Active Directory


class User(Base):
    """Modelo de Usuario con funcionalidades avanzadas"""
    __tablename__ = "users"
    
    # Identificadores
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), index=True)
    
    # Información básica
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    
    # Autenticación
    hashed_password = Column(String(255), nullable=True)  # Nullable para OAuth users
    auth_provider = Column(SQLEnum(AuthProvider), default=AuthProvider.LOCAL, nullable=False)
    external_id = Column(String(255), nullable=True, index=True)  # ID del proveedor externo
    
    # Estado y roles
    status = Column(SQLEnum(UserStatus), default=UserStatus.PENDING, index=True)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, index=True)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Información de contacto
    phone = Column(String(20), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    timezone = Column(String(50), default='UTC', nullable=False)
    language = Column(String(10), default='es', nullable=False)
    
    # Organización
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=True, index=True)
    department = Column(String(100), nullable=True)
    job_title = Column(String(100), nullable=True)
    
    # Configuraciones del usuario
    preferences = Column(JSON, nullable=True)  # Preferencias de UI, notificaciones, etc.
    permissions = Column(JSON, nullable=True)  # Permisos específicos del usuario
    
    # Timestamps y actividad
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True, index=True)
    last_activity = Column(DateTime(timezone=True), nullable=True)
    password_changed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Verificación y seguridad
    email_verified_at = Column(DateTime(timezone=True), nullable=True)
    phone_verified_at = Column(DateTime(timezone=True), nullable=True)
    two_factor_enabled = Column(Boolean, default=False, nullable=False)
    two_factor_secret = Column(String(255), nullable=True)
    
    # Estadísticas de uso
    documents_processed = Column(Integer, default=0, nullable=False)
    total_processing_time = Column(Float, default=0.0, nullable=False)  # En segundos
    last_document_processed = Column(DateTime(timezone=True), nullable=True)
    
    # Límites y cuotas
    daily_document_limit = Column(Integer, nullable=True)
    monthly_document_limit = Column(Integer, nullable=True)
    storage_limit_mb = Column(Integer, nullable=True)
    
    # Soft delete
    is_deleted = Column(Boolean, default=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relaciones
    organization = relationship("Organization", back_populates="users")
    documents = relationship("Document", foreign_keys="Document.user_id", back_populates="user")
    reviewed_documents = relationship("Document", foreign_keys="Document.reviewed_by")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship("ApiKey", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")
    
    # Índices compuestos optimizados
    __table_args__ = (
        # Índices para filtrado por organización y rol
        Index('ix_users_org_role', 'organization_id', 'role'),
        Index('ix_users_org_status', 'organization_id', 'status'),
        Index('ix_users_org_active', 'organization_id', 'is_deleted'),
        
        # Índices para filtrado por estado
        Index('ix_users_status_created', 'status', 'created_at'),
        Index('ix_users_status_active', 'status', 'is_deleted'),
        Index('ix_users_active_deleted', 'is_deleted', 'created_at'),
        
        # Índices para autenticación
        Index('ix_users_provider_external', 'auth_provider', 'external_id'),
        Index('ix_users_email_active', 'email', 'is_deleted'),
        Index('ix_users_username_active', 'username', 'is_deleted'),
        
        # Índices para actividad
        Index('ix_users_last_login', 'last_login'),
        Index('ix_users_last_activity', 'last_activity'),
        
        # Constraint único para OAuth
        UniqueConstraint('auth_provider', 'external_id', name='uq_user_provider_external'),
    )
    
    @validates('email')
    def validate_email(self, key, email):
        """Validar formato de email"""
        import re
        if not email or not isinstance(email, str):
            raise ValueError("email no puede estar vacío")
        email = email.strip().lower()
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValueError("Formato de email inválido")
        if len(email) > 255:
            raise ValueError("email excede la longitud máxima")
        return email
    
    @validates('username')
    def validate_username(self, key, username):
        """Validar formato de username"""
        import re
        if not username or not isinstance(username, str):
            raise ValueError("username no puede estar vacío")
        username = username.strip()
        if not re.match(r'^[a-zA-Z0-9_-]{3,30}$', username):
            raise ValueError("Username debe tener 3-30 caracteres alfanuméricos, guiones o guiones bajos")
        # Validar que no empiece con guión
        if username.startswith('-') or username.startswith('_'):
            raise ValueError("Username no puede empezar con guión o guión bajo")
        return username.lower()
    
    @validates('phone')
    def validate_phone(self, key, value):
        """Validar formato de teléfono"""
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError("phone debe ser una cadena de texto")
        # Remover espacios y caracteres especiales para validación
        cleaned = ''.join(filter(str.isdigit, value))
        if len(cleaned) < 7 or len(cleaned) > 15:
            raise ValueError("phone debe tener entre 7 y 15 dígitos")
        return value
    
    @validates('timezone')
    def validate_timezone(self, key, value):
        """Validar timezone"""
        if not value:
            return 'UTC'
        # Lista básica de timezones comunes
        common_timezones = [
            'UTC', 'America/New_York', 'America/Chicago', 'America/Denver',
            'America/Los_Angeles', 'Europe/London', 'Europe/Paris', 'Europe/Madrid',
            'Asia/Tokyo', 'Asia/Shanghai', 'Australia/Sydney'
        ]
        # Validación básica (en producción usar pytz o zoneinfo)
        if '/' in value or value in common_timezones:
            return value
        return 'UTC'  # Default seguro
    
    @hybrid_property
    def is_active(self):
        """Indica si el usuario está activo"""
        return self.status == UserStatus.ACTIVE and not self.is_deleted
    
    @hybrid_property
    def is_admin(self):
        """Indica si el usuario es administrador"""
        return self.role == UserRole.ADMIN or self.is_superuser
    
    @hybrid_property
    def can_process_documents(self):
        """Indica si el usuario puede procesar documentos"""
        return self.role in [UserRole.ADMIN, UserRole.MANAGER, UserRole.OPERATOR] and self.is_active
    
    @hybrid_property
    def can_review_documents(self):
        """Indica si el usuario puede revisar documentos"""
        return self.role in [UserRole.ADMIN, UserRole.MANAGER, UserRole.REVIEWER] and self.is_active
    
    @hybrid_property
    def full_display_name(self):
        """Nombre completo para mostrar"""
        if self.full_name:
            return self.full_name
        elif self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        else:
            return self.username
    
    @hybrid_property
    def needs_password_change(self):
        """Indica si necesita cambiar contraseña (más de 90 días)"""
        if not self.password_changed_at:
            return True
        return (datetime.utcnow() - self.password_changed_at).days > 90
    
    @hybrid_property
    def average_processing_time(self):
        """Tiempo promedio de procesamiento por documento"""
        if self.documents_processed > 0 and self.total_processing_time > 0:
            return self.total_processing_time / self.documents_processed
        return None
    
    @hybrid_property
    def inactivity_days(self):
        """Días de inactividad"""
        if self.last_activity:
            return (datetime.utcnow() - self.last_activity).days
        elif self.last_login:
            return (datetime.utcnow() - self.last_login).days
        return None
    
    @hybrid_property
    def is_inactive(self):
        """Indica si el usuario está inactivo (más de 30 días)"""
        inactivity = self.inactivity_days
        return inactivity is not None and inactivity > 30
    
    @hybrid_property
    def account_age_days(self):
        """Edad de la cuenta en días"""
        if self.created_at:
            return (datetime.utcnow() - self.created_at).days
        return None
    
    def to_dict(self, include_sensitive=False) -> Dict[str, Any]:
        """Convierte el usuario a diccionario"""
        data = {
            "id": self.id,
            "uuid": self.uuid,
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_display_name": self.full_display_name,
            "status": self.status.value,
            "role": self.role.value,
            "auth_provider": self.auth_provider.value,
            "is_verified": self.is_verified,
            "is_superuser": self.is_superuser,
            "phone": self.phone,
            "avatar_url": self.avatar_url,
            "timezone": self.timezone,
            "language": self.language,
            "department": self.department,
            "job_title": self.job_title,
            "organization_id": self.organization_id,
            "documents_processed": self.documents_processed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "is_active": self.is_active,
            "can_process_documents": self.can_process_documents,
            "can_review_documents": self.can_review_documents,
        }
        
        if include_sensitive:
            data.update({
                "preferences": self.preferences,
                "permissions": self.permissions,
                "two_factor_enabled": self.two_factor_enabled,
                "email_verified_at": self.email_verified_at.isoformat() if self.email_verified_at else None,
                "needs_password_change": self.needs_password_change,
            })
        
        return data
    
    def has_permission(self, permission: str) -> bool:
        """Verifica si el usuario tiene un permiso específico"""
        if self.is_superuser:
            return True
        
        # Permisos por rol
        role_permissions = {
            UserRole.ADMIN: ['*'],  # Todos los permisos
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
        
        # Verificar permisos por rol
        if self.role in role_permissions:
            if '*' in role_permissions[self.role] or permission in role_permissions[self.role]:
                return True
        
        # Verificar permisos específicos del usuario
        if self.permissions and isinstance(self.permissions, dict):
            user_perms = self.permissions.get('permissions', [])
            if permission in user_perms:
                return True
        
        return False
    
    def update_activity(self):
        """Actualiza la última actividad del usuario"""
        self.last_activity = datetime.utcnow()
    
    def update_login(self):
        """Actualiza la información de último login"""
        self.last_login = datetime.utcnow()
        self.update_activity()
    
    def increment_documents_processed(self, processing_time: float = 0):
        """Incrementa el contador de documentos procesados"""
        self.documents_processed += 1
        self.total_processing_time += processing_time
        self.last_document_processed = datetime.utcnow()
    
    def can_process_more_documents(self, session=None) -> bool:
        """Verifica si puede procesar más documentos según límites"""
        if not self.daily_document_limit and not self.monthly_document_limit:
            return True
        
        if not session:
            # Sin sesión, asumir que puede procesar
            return True
        
        from sqlalchemy import and_, func
        from .document_enhanced import Document, DocumentStatus
        
        # Verificar límite diario
        if self.daily_document_limit:
            today = datetime.utcnow().date()
            daily_count = session.query(Document).filter(
                and_(
                    Document.user_id == self.id,
                    func.date(Document.created_at) == today,
                    Document.status.in_([DocumentStatus.PROCESSED, DocumentStatus.APPROVED])
                )
            ).count()
            if daily_count >= self.daily_document_limit:
                return False
        
        # Verificar límite mensual
        if self.monthly_document_limit:
            from datetime import date
            first_day_month = date.today().replace(day=1)
            monthly_count = session.query(Document).filter(
                and_(
                    Document.user_id == self.id,
                    func.date(Document.created_at) >= first_day_month,
                    Document.status.in_([DocumentStatus.PROCESSED, DocumentStatus.APPROVED])
                )
            ).count()
            if monthly_count >= self.monthly_document_limit:
                return False
        
        return True
    
    def check_storage_limit(self, additional_mb: float = 0, session=None) -> bool:
        """Verifica si puede usar más almacenamiento"""
        if not self.storage_limit_mb:
            return True
        
        if not session:
            return True
        
        from sqlalchemy import func
        from .document_enhanced import Document
        
        # Calcular almacenamiento actual
        total_size = session.query(
            func.sum(Document.file_size)
        ).filter(
            Document.user_id == self.id,
            Document.is_deleted == False
        ).scalar() or 0
        
        total_mb = (total_size / (1024 * 1024)) + additional_mb
        return total_mb <= self.storage_limit_mb
    
    def get_usage_stats(self, session=None) -> Dict[str, Any]:
        """Obtiene estadísticas de uso del usuario"""
        if not session:
            return {}
        
        from sqlalchemy import func
        from .document_enhanced import Document, DocumentStatus
        
        stats = {
            "total_documents": session.query(Document).filter(
                Document.user_id == self.id,
                Document.is_deleted == False
            ).count(),
            "processed_documents": session.query(Document).filter(
                Document.user_id == self.id,
                Document.status.in_([DocumentStatus.PROCESSED, DocumentStatus.APPROVED]),
                Document.is_deleted == False
            ).count(),
            "pending_documents": session.query(Document).filter(
                Document.user_id == self.id,
                Document.status == DocumentStatus.UPLOADED,
                Document.is_deleted == False
            ).count(),
            "total_storage_mb": 0,
            "average_confidence": None,
        }
        
        # Calcular almacenamiento
        total_size = session.query(func.sum(Document.file_size)).filter(
            Document.user_id == self.id,
            Document.is_deleted == False
        ).scalar() or 0
        stats["total_storage_mb"] = total_size / (1024 * 1024)
        
        # Calcular confianza promedio
        avg_conf = session.query(func.avg(Document.confidence_score)).filter(
            Document.user_id == self.id,
            Document.confidence_score.isnot(None),
            Document.is_deleted == False
        ).scalar()
        stats["average_confidence"] = float(avg_conf) if avg_conf else None
        
        return stats
    
    def soft_delete(self):
        """Eliminación lógica del usuario"""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        self.status = UserStatus.INACTIVE
    
    def restore(self):
        """Restaura un usuario eliminado lógicamente"""
        self.is_deleted = False
        self.deleted_at = None
        if self.status == UserStatus.INACTIVE:
            self.status = UserStatus.ACTIVE
    
    def suspend(self, reason: str = None):
        """Suspende al usuario"""
        self.status = UserStatus.SUSPENDED
        if reason:
            # Guardar razón en preferences o crear campo específico
            if not self.preferences:
                self.preferences = {}
            self.preferences['suspension_reason'] = reason
    
    def activate(self):
        """Activa al usuario"""
        if self.status in [UserStatus.PENDING, UserStatus.INACTIVE]:
            self.status = UserStatus.ACTIVE
            self.is_verified = True
    
    def verify_email(self):
        """Marca el email como verificado"""
        self.is_verified = True
        self.email_verified_at = datetime.utcnow()
    
    def verify_phone(self):
        """Marca el teléfono como verificado"""
        self.phone_verified_at = datetime.utcnow()
    
    def update_password(self, new_hashed_password: str):
        """Actualiza la contraseña"""
        self.hashed_password = new_hashed_password
        self.password_changed_at = datetime.utcnow()
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role.value}')>"


class UserSession(Base):
    """Sesiones de usuario para tracking y seguridad"""
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    
    # Información de la sesión
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    device_info = Column(JSON, nullable=True)
    location_info = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    # Estado
    is_active = Column(Boolean, default=True, nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relaciones
    user = relationship("User", back_populates="sessions")
    
    __table_args__ = (
        Index('ix_sessions_user_active', 'user_id', 'is_active'),
        Index('ix_sessions_expires', 'expires_at'),
    )
    
    @hybrid_property
    def is_expired(self):
        """Indica si la sesión ha expirado"""
        return datetime.utcnow() > self.expires_at
    
    @hybrid_property
    def is_valid(self):
        """Indica si la sesión es válida"""
        return self.is_active and not self.is_expired and not self.revoked_at
    
    def revoke(self):
        """Revoca la sesión"""
        self.is_active = False
        self.revoked_at = datetime.utcnow()


class ApiKey(Base):
    """API Keys para acceso programático"""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    # Información de la API Key
    name = Column(String(100), nullable=False)
    key_hash = Column(String(255), unique=True, nullable=False, index=True)
    key_prefix = Column(String(10), nullable=False, index=True)  # Primeros caracteres para identificación
    
    # Permisos y límites
    permissions = Column(JSON, nullable=True)  # Permisos específicos de esta key
    rate_limit_per_minute = Column(Integer, nullable=True)
    rate_limit_per_day = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Estado
    is_active = Column(Boolean, default=True, nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    
    # Estadísticas de uso
    usage_count = Column(Integer, default=0, nullable=False)
    
    # Relaciones
    user = relationship("User", back_populates="api_keys")
    
    __table_args__ = (
        Index('ix_apikeys_user_active', 'user_id', 'is_active'),
    )
    
    @hybrid_property
    def is_expired(self):
        """Indica si la API key ha expirado"""
        return self.expires_at and datetime.utcnow() > self.expires_at
    
    @hybrid_property
    def is_valid(self):
        """Indica si la API key es válida"""
        return self.is_active and not self.is_expired and not self.revoked_at
    
    def increment_usage(self):
        """Incrementa el contador de uso"""
        self.usage_count += 1
        self.last_used = datetime.utcnow()
    
    def revoke(self):
        """Revoca la API key"""
        self.is_active = False
        self.revoked_at = datetime.utcnow()


class AuditLog(Base):
    """Log de auditoría para tracking de acciones"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    
    # Información de la acción
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False, index=True)
    resource_id = Column(String(100), nullable=True, index=True)
    
    # Detalles
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relaciones
    user = relationship("User", back_populates="audit_logs")
    
    __table_args__ = (
        Index('ix_audit_action_resource', 'action', 'resource_type'),
        Index('ix_audit_user_created', 'user_id', 'created_at'),
    )

















