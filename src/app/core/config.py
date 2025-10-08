from pydantic_settings import BaseSettings
from pathlib import Path
import os

class Settings(BaseSettings):
    APP_NAME: str = "Document Extractor API - Optimized"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8005
    
    # Base de datos - PostgreSQL por defecto, SQLite como fallback
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/document_extractor"
    DATABASE_URL_TEST: str = "postgresql://postgres:postgres@localhost:5432/document_extractor_test"
    DATABASE_URL_FALLBACK: str = "sqlite:///./data/documents.db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # Directorios
    UPLOAD_DIR: str = "uploads"
    OUTPUT_DIR: str = "outputs"
    
    # Tesseract
    TESSERACT_CMD: str = ""
    
    # Configuración de base de datos
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 30
    DB_POOL_PRE_PING: bool = True
    DB_POOL_RECYCLE: int = 3600
    
    # Configuración OCR
    GOOGLE_VISION_DAILY_LIMIT: int = 200
    AWS_TEXTRACT_DAILY_LIMIT: int = 100
    TESSERACT_CONFIDENCE_THRESHOLD: float = 0.7
    
    # Configuración LLM
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_MAX_TOKENS: int = 1000
    OPENAI_TEMPERATURE: float = 0
    
    # Configuración AWS
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    
    # Configuración Google Cloud
    GOOGLE_APPLICATION_CREDENTIALS: str = ""
    
    # Procesamiento asíncrono
    RQ_WORKER_TIMEOUT: int = 600  # 10 minutos
    RQ_QUEUE_NAME: str = "document_processing"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Crear directorios necesarios
settings = Settings()
Path(settings.UPLOAD_DIR).mkdir(exist_ok=True)
Path(settings.OUTPUT_DIR).mkdir(exist_ok=True)
Path("data").mkdir(exist_ok=True)

# Configurar Tesseract si es necesario
if settings.TESSERACT_CMD:
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD
