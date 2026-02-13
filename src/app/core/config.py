"""
Wrapper de compatibilidad para config.py legacy
DEPRECATED: Usar environment.py en su lugar

Este archivo mantiene compatibilidad con código legacy mientras
se migra a environment.py. Se eliminará en versión 3.0.0.
"""
import warnings
from typing import TYPE_CHECKING
from pathlib import Path

if TYPE_CHECKING:
    from .environment import AppConfig

from .environment import get_settings

# Obtener settings una vez
_settings = get_settings()

class Settings:
    """
    Wrapper de compatibilidad para config.py legacy
    DEPRECATED: Usar get_settings() de environment.py
    """
    
    def __init__(self):
        warnings.warn(
            "config.Settings está deprecado. Usa environment.get_settings()",
            DeprecationWarning,
            stacklevel=2
        )
        self._settings = _settings
    
    # Mapeo de propiedades legacy a nuevas
    @property
    def APP_NAME(self) -> str:
        return self._settings.name
    
    @property
    def DEBUG(self) -> bool:
        return self._settings.debug
    
    @property
    def HOST(self) -> str:
        return self._settings.host
    
    @property
    def PORT(self) -> int:
        return self._settings.port
    
    @property
    def DATABASE_URL(self) -> str:
        return self._settings.database.url
    
    @property
    def DATABASE_URL_TEST(self) -> str:
        return self._settings.database.url_test
    
    @property
    def DATABASE_URL_FALLBACK(self) -> str:
        return self._settings.database.url_fallback
    
    @property
    def REDIS_HOST(self) -> str:
        return self._settings.redis.host
    
    @property
    def REDIS_PORT(self) -> int:
        return self._settings.redis.port
    
    @property
    def REDIS_DB(self) -> int:
        return self._settings.redis.db
    
    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self._settings.redis.host}:{self._settings.redis.port}/{self._settings.redis.db}"
    
    @property
    def UPLOAD_DIR(self) -> str:
        return self._settings.upload_dir
    
    @property
    def OUTPUT_DIR(self) -> str:
        return self._settings.output_dir
    
    @property
    def TESSERACT_CMD(self) -> str:
        return self._settings.ocr.tesseract_cmd
    
    @property
    def GOOGLE_VISION_DAILY_LIMIT(self) -> int:
        return self._settings.ocr.google_vision_daily_limit
    
    @property
    def AWS_TEXTRACT_DAILY_LIMIT(self) -> int:
        return self._settings.ocr.aws_textract_daily_limit
    
    @property
    def TESSERACT_CONFIDENCE_THRESHOLD(self) -> float:
        return self._settings.ocr.confidence_threshold
    
    @property
    def OPENAI_API_KEY(self) -> str:
        return self._settings.llm.openai_api_key or ""
    
    @property
    def OPENAI_MODEL(self) -> str:
        return self._settings.llm.openai_model
    
    @property
    def OPENAI_MAX_TOKENS(self) -> int:
        return self._settings.llm.openai_max_tokens
    
    @property
    def OPENAI_TEMPERATURE(self) -> float:
        return self._settings.llm.openai_temperature
    
    @property
    def AWS_ACCESS_KEY_ID(self) -> str:
        return self._settings.ocr.aws_access_key_id or ""
    
    @property
    def AWS_SECRET_ACCESS_KEY(self) -> str:
        return self._settings.ocr.aws_secret_access_key or ""
    
    @property
    def AWS_REGION(self) -> str:
        return self._settings.ocr.aws_region
    
    @property
    def GOOGLE_APPLICATION_CREDENTIALS(self) -> str:
        return self._settings.ocr.google_application_credentials or ""
    
    @property
    def RQ_WORKER_TIMEOUT(self) -> int:
        return self._settings.rq_worker_timeout
    
    @property
    def RQ_QUEUE_NAME(self) -> str:
        return self._settings.rq_queue_name
    
    @property
    def SECRET_KEY(self) -> str:
        return self._settings.security.secret_key
    
    @property
    def ALGORITHM(self) -> str:
        return self._settings.security.algorithm
    
    @property
    def ACCESS_TOKEN_EXPIRE_MINUTES(self) -> int:
        return self._settings.security.access_token_expire_minutes
    
    @property
    def REFRESH_TOKEN_EXPIRE_DAYS(self) -> int:
        return getattr(self._settings.security, 'refresh_token_expire_days', 7)
    
    @property
    def RATE_LIMIT_PER_MINUTE(self) -> int:
        return self._settings.security.rate_limit_per_minute
    
    @property
    def RATE_LIMIT_BURST(self) -> int:
        return self._settings.security.rate_limit_burst
    
    @property
    def DB_POOL_SIZE(self) -> int:
        return self._settings.database.pool_size
    
    @property
    def DB_MAX_OVERFLOW(self) -> int:
        return self._settings.database.max_overflow
    
    @property
    def DB_POOL_PRE_PING(self) -> bool:
        return self._settings.database.pool_pre_ping
    
    @property
    def DB_POOL_RECYCLE(self) -> int:
        return self._settings.database.pool_recycle

# Instancia singleton para compatibilidad
settings = Settings()

# Crear directorios necesarios (mantener funcionalidad)
Path(_settings.upload_dir).mkdir(exist_ok=True)
Path(_settings.output_dir).mkdir(exist_ok=True)
Path("data").mkdir(exist_ok=True)

# Configurar Tesseract si es necesario (mantener funcionalidad)
if _settings.ocr.tesseract_cmd:
    try:
        import pytesseract
        pytesseract.pytesseract.tesseract_cmd = _settings.ocr.tesseract_cmd
    except ImportError:
        pass
