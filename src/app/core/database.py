from sqlalchemy import create_engine, MetaData, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from app.core.config import settings
import redis
import logging

logger = logging.getLogger(__name__)

# Crear motor de base de datos con fallback a SQLite
try:
    # Intentar con PostgreSQL primero
    if "postgresql" in settings.DATABASE_URL:
        engine = create_engine(
            settings.DATABASE_URL,
            poolclass=QueuePool,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            pool_pre_ping=settings.DB_POOL_PRE_PING,
            pool_recycle=settings.DB_POOL_RECYCLE,
            echo=settings.DEBUG,
        )
        logger.info("Conectado a PostgreSQL")
    else:
        # Usar SQLite como fallback
        engine = create_engine(
            settings.DATABASE_URL,
            connect_args={"check_same_thread": False},
            echo=settings.DEBUG,
        )
        logger.info("Conectado a SQLite")
except Exception as e:
    # Fallback a SQLite si PostgreSQL falla
    logger.warning(f"Error conectando a PostgreSQL: {e}")
    logger.info("Usando SQLite como fallback")
    engine = create_engine(
        settings.DATABASE_URL_FALLBACK,
        connect_args={"check_same_thread": False},
        echo=settings.DEBUG,
    )

# Crear sesión
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base para modelos
Base = declarative_base()

# Metadata
metadata = MetaData()

# Cliente Redis
try:
    redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        decode_responses=True
    )
    # Test connection
    redis_client.ping()
    logger.info("Redis conectado correctamente")
except Exception as e:
    logger.warning(f"Redis no disponible: {e}")
    redis_client = None

def get_db():
    """Dependency para obtener sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_redis():
    """Dependency para obtener cliente Redis"""
    return redis_client
