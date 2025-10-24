"""
Configuración de Logging
========================

Sistema de logging centralizado y optimizado.
"""
import logging
import logging.config
import sys
from pathlib import Path
from typing import Dict, Any

from .environment import get_settings


def setup_logging() -> None:
    """Configurar sistema de logging"""
    settings = get_settings()
    
    # Crear directorio de logs si no existe
    log_dir = Path(settings.log_dir)
    log_dir.mkdir(exist_ok=True)
    
    # Configuración de logging
    logging_config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "format": '{"timestamp": "%(asctime)s", "logger": "%(name)s", "level": "%(levelname)s", "module": "%(module)s", "function": "%(funcName)s", "line": %(lineno)d, "message": "%(message)s"}',
                "datefmt": "%Y-%m-%dT%H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG" if settings.debug else "INFO",
                "formatter": "default",
                "stream": sys.stdout,
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "detailed",
                "filename": log_dir / "app.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "detailed",
                "filename": log_dir / "error.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            },
        },
        "loggers": {
            "": {  # Root logger
                "level": "DEBUG" if settings.debug else "INFO",
                "handlers": ["console", "file", "error_file"],
                "propagate": False,
            },
            "app": {
                "level": "DEBUG" if settings.debug else "INFO",
                "handlers": ["console", "file", "error_file"],
                "propagate": False,
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "sqlalchemy": {
                "level": "WARNING",
                "handlers": ["file"],
                "propagate": False,
            },
            "redis": {
                "level": "WARNING",
                "handlers": ["file"],
                "propagate": False,
            },
        },
    }
    
    # Aplicar configuración
    logging.config.dictConfig(logging_config)
    
    # Configurar logger principal
    logger = logging.getLogger("app")
    logger.info(f"Logging configurado para ambiente: {settings.environment.value}")


def get_logger(name: str) -> logging.Logger:
    """Obtener logger con nombre específico"""
    return logging.getLogger(f"app.{name}")


class LoggerMixin:
    """Mixin para agregar logging a cualquier clase"""
    
    @property
    def logger(self) -> logging.Logger:
        """Logger para la clase"""
        return get_logger(self.__class__.__name__)
