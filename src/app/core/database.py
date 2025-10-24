"""
Sistema de Base de Datos Optimizado
===================================

Sistema robusto de conexión a base de datos con fallbacks y optimizaciones.
"""
import asyncio
import logging
from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager

from sqlalchemy import create_engine, MetaData, Index, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool, StaticPool
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

import redis
from redis.exceptions import RedisError

from .environment import get_settings, get_database_url

logger = logging.getLogger(__name__)

# Configuración
settings = get_settings()

# Variables globales
engine: Optional[Engine] = None
SessionLocal: Optional[sessionmaker] = None
redis_client: Optional[redis.Redis] = None

# Base para modelos
Base = declarative_base()

# Metadata
metadata = MetaData()


def create_database_engine() -> Engine:
    """Crear motor de base de datos optimizado"""
    global engine
    
    if engine is not None:
        return engine
    
    try:
        database_url = get_database_url()
        logger.info(f"Conectando a base de datos: {database_url.split('@')[-1] if '@' in database_url else database_url}")
        
        # Configuración según el tipo de base de datos
        if "postgresql" in database_url:
            engine = create_engine(
                database_url,
                poolclass=QueuePool,
                pool_size=settings.database.pool_size,
                max_overflow=settings.database.max_overflow,
                pool_pre_ping=settings.database.pool_pre_ping,
                pool_recycle=settings.database.pool_recycle,
                echo=settings.debug,
                # Optimizaciones adicionales
                pool_reset_on_return='commit',
                pool_timeout=30,
            )
            logger.info("✅ Conectado a PostgreSQL")
            
        elif "sqlite" in database_url:
            engine = create_engine(
                database_url,
                poolclass=StaticPool,
                connect_args={
                    "check_same_thread": False,
                    "timeout": 30,
                },
                echo=settings.debug,
            )
            logger.info("✅ Conectado a SQLite")
            
        else:
            raise ValueError(f"Tipo de base de datos no soportado: {database_url}")
        
        # Eventos de conexión para logging
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            if "sqlite" in database_url:
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.close()
        
        return engine
        
    except Exception as e:
        logger.error(f"❌ Error creando motor de base de datos: {e}")
        
        # Fallback a SQLite
        if "sqlite" not in database_url:
            logger.warning("🔄 Intentando fallback a SQLite...")
            try:
                fallback_url = settings.database.url_fallback
                engine = create_engine(
                    fallback_url,
                    poolclass=StaticPool,
                    connect_args={"check_same_thread": False},
                    echo=settings.debug,
                )
                logger.info("✅ Fallback a SQLite exitoso")
                return engine
            except Exception as fallback_error:
                logger.error(f"❌ Fallback a SQLite falló: {fallback_error}")
                raise
        
        raise


def create_session_factory() -> sessionmaker:
    """Crear factory de sesiones"""
    global SessionLocal
    
    if SessionLocal is not None:
        return SessionLocal
    
    engine = create_database_engine()
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        expire_on_commit=False,  # Evitar problemas con objetos detached
    )
    
    return SessionLocal


def create_redis_client() -> Optional[redis.Redis]:
    """Crear cliente Redis"""
    global redis_client
    
    if redis_client is not None:
        return redis_client
    
    try:
        redis_client = redis.Redis(
            host=settings.redis.host,
            port=settings.redis.port,
            db=settings.redis.db,
            password=settings.redis.password,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30,
        )
        
        # Test de conexión
        redis_client.ping()
        logger.info("✅ Conectado a Redis")
        return redis_client
        
    except RedisError as e:
        logger.warning(f"⚠️ Redis no disponible: {e}")
        redis_client = None
        return None
    except Exception as e:
        logger.error(f"❌ Error creando cliente Redis: {e}")
        redis_client = None
        return None


async def init_database() -> None:
    """Inicializar base de datos"""
    try:
        # Crear motor y sesión
        create_database_engine()
        create_session_factory()
        
        # Crear tablas
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tablas de base de datos creadas/verificadas")
        
        # Inicializar Redis
        create_redis_client()
        
    except Exception as e:
        logger.error(f"❌ Error inicializando base de datos: {e}")
        raise


async def close_database() -> None:
    """Cerrar conexiones de base de datos"""
    global engine, redis_client
    
    try:
        if engine:
            engine.dispose()
            logger.info("✅ Conexiones de base de datos cerradas")
        
        if redis_client:
            redis_client.close()
            logger.info("✅ Conexión Redis cerrada")
            
    except Exception as e:
        logger.error(f"❌ Error cerrando conexiones: {e}")


def get_db() -> AsyncGenerator[Session, None]:
    """Dependency para obtener sesión de base de datos"""
    if SessionLocal is None:
        create_session_factory()
    
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Error en sesión de base de datos: {e}")
        db.rollback()
        raise
    finally:
        db.close()


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[Session, None]:
    """Context manager para sesión de base de datos"""
    if SessionLocal is None:
        create_session_factory()
    
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error en transacción: {e}")
        raise
    finally:
        db.close()


# Funciones de utilidad
def get_redis() -> Optional[redis.Redis]:
    """Obtener cliente Redis"""
    if redis_client is None:
        create_redis_client()
    return redis_client


def is_database_healthy() -> bool:
    """Verificar salud de la base de datos"""
    try:
        if engine is None:
            return False
        
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


def is_redis_healthy() -> bool:
    """Verificar salud de Redis"""
    try:
        if redis_client is None:
            return False
        
        redis_client.ping()
        return True
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return False