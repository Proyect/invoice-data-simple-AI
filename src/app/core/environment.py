"""
Configuración de Ambientes
=========================

Sistema robusto de configuración por ambientes con validación.
"""
from enum import Enum
from pathlib import Path
from typing import Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Environment(str, Enum):
    """Ambientes disponibles"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class DatabaseConfig(BaseSettings):
    """Configuración de base de datos"""
    url: str = Field(..., env="DATABASE_URL")
    url_test: str = Field(..., env="DATABASE_URL_TEST")
    url_fallback: str = Field(default="sqlite:///./data/documents.db", env="DATABASE_URL_FALLBACK")
    
    # Pool de conexiones
    pool_size: int = Field(default=20, ge=1, le=100)
    max_overflow: int = Field(default=30, ge=0, le=100)
    pool_pre_ping: bool = Field(default=True)
    pool_recycle: int = Field(default=3600, ge=300)
    
    @validator('url', 'url_test')
    def validate_database_url(cls, v):
        if not v:
            raise ValueError("Database URL is required")
        return v


class RedisConfig(BaseSettings):
    """Configuración de Redis"""
    url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    host: str = Field(default="localhost", env="REDIS_HOST")
    port: int = Field(default=6379, ge=1, le=65535, env="REDIS_PORT")
    db: int = Field(default=0, ge=0, le=15, env="REDIS_DB")
    password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")


class OCRConfig(BaseSettings):
    """Configuración de OCR"""
    tesseract_cmd: str = Field(default="", env="TESSERACT_CMD")
    confidence_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    
    # Límites diarios
    google_vision_daily_limit: int = Field(default=200, ge=0)
    aws_textract_daily_limit: int = Field(default=100, ge=0)
    
    # Google Cloud
    google_application_credentials: Optional[str] = Field(default=None, env="GOOGLE_APPLICATION_CREDENTIALS")
    
    # AWS
    aws_access_key_id: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    aws_region: str = Field(default="us-east-1", env="AWS_REGION")


class LLMConfig(BaseSettings):
    """Configuración de LLM"""
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-3.5-turbo")
    openai_max_tokens: int = Field(default=1000, ge=1, le=4000)
    openai_temperature: float = Field(default=0.0, ge=0.0, le=2.0)


class SecurityConfig(BaseSettings):
    """Configuración de seguridad"""
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30, ge=1, le=1440)
    
    @validator('secret_key')
    def validate_secret_key(cls, v):
        if not v or v == "your-super-secret-key-change-this-in-production":
            raise ValueError("SECRET_KEY must be set to a secure value")
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v


class AppConfig(BaseSettings):
    """Configuración principal de la aplicación"""
    name: str = Field(default="Document Extractor API - Optimized", env="APP_NAME")
    version: str = Field(default="2.0.0")
    environment: Environment = Field(default=Environment.DEVELOPMENT, env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8005, ge=1, le=65535, env="PORT")
    
    # Directorios
    upload_dir: str = Field(default="uploads", env="UPLOAD_DIR")
    output_dir: str = Field(default="outputs", env="OUTPUT_DIR")
    log_dir: str = Field(default="logs", env="LOG_DIR")
    
    # Procesamiento asíncrono
    rq_worker_timeout: int = Field(default=600, ge=60, env="RQ_WORKER_TIMEOUT")
    rq_queue_name: str = Field(default="document_processing", env="RQ_QUEUE_NAME")
    
    # Configuraciones anidadas
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    ocr: OCRConfig = Field(default_factory=OCRConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        validate_assignment = True
    
    @validator('environment', pre=True)
    def validate_environment(cls, v):
        if isinstance(v, str):
            try:
                return Environment(v.lower())
            except ValueError:
                raise ValueError(f"Invalid environment: {v}. Must be one of: {list(Environment)}")
        return v
    
    @validator('debug')
    def validate_debug_for_production(cls, v, values):
        if values.get('environment') == Environment.PRODUCTION and v:
            raise ValueError("DEBUG cannot be True in production environment")
        return v


def get_settings() -> AppConfig:
    """Obtener configuración de la aplicación"""
    return AppConfig()


def get_database_url(environment: Environment = None) -> str:
    """Obtener URL de base de datos según el ambiente"""
    settings = get_settings()
    env = environment or settings.environment
    
    if env == Environment.TESTING:
        return settings.database.url_test
    elif env == Environment.PRODUCTION:
        return settings.database.url
    else:
        # Development/Staging - intentar PostgreSQL, fallback a SQLite
        try:
            return settings.database.url
        except:
            return settings.database.url_fallback
