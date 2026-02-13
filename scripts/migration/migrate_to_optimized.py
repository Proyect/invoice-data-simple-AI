#!/usr/bin/env python3
"""
Script de Migración al Sistema Optimizado
==========================================

Script para migrar desde el sistema actual al sistema optimizado.
"""
import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.app.core.environment import get_settings
from src.app.core.database import init_database, create_database_engine, create_session_factory
from src.app.models.document_unified import Document
from src.app.models.base import Base

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def backup_existing_data():
    """Hacer backup de datos existentes"""
    logger.info("🔄 Creando backup de datos existentes...")
    
    try:
        # Crear directorio de backup
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        
        # Backup de base de datos SQLite si existe
        db_path = Path("data/documents.db")
        if db_path.exists():
            backup_file = backup_dir / f"documents_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            import shutil
            shutil.copy2(db_path, backup_file)
            logger.info(f"✅ Backup creado: {backup_file}")
        
        # Backup de archivos de configuración
        config_files = ["config_ejemplo.env", "config_gratuito.env", "config_minimo.env", "config_optimo.env"]
        for config_file in config_files:
            if Path(config_file).exists():
                backup_file = backup_dir / f"{config_file}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy2(config_file, backup_file)
                logger.info(f"✅ Backup de configuración: {backup_file}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creando backup: {e}")
        return False


def migrate_database_schema():
    """Migrar esquema de base de datos"""
    logger.info("🔄 Migrando esquema de base de datos...")
    
    try:
        # Inicializar base de datos
        import asyncio
        asyncio.run(init_database())
        
        # Crear motor y sesión
        engine = create_database_engine()
        SessionLocal = create_session_factory()
        
        # Crear tablas del nuevo esquema
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Esquema de base de datos migrado")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error migrando esquema: {e}")
        return False


def migrate_existing_documents():
    """Migrar documentos existentes al nuevo esquema"""
    logger.info("🔄 Migrando documentos existentes...")
    
    try:
        from sqlalchemy import text
        from src.app.models.document import Document as OldDocument
        
        # Crear sesión
        SessionLocal = create_session_factory()
        db = SessionLocal()
        
        # Verificar si existen documentos en el esquema anterior
        try:
            old_documents = db.query(OldDocument).all()
            logger.info(f"📊 Encontrados {len(old_documents)} documentos en esquema anterior")
            
            if old_documents:
                # Migrar documentos
                migrated_count = 0
                for old_doc in old_documents:
                    try:
                        # Crear nuevo documento
                        new_doc = Document(
                            filename=old_doc.filename,
                            original_filename=old_doc.original_filename,
                            file_path=old_doc.file_path,
                            file_size=old_doc.file_size,
                            mime_type=old_doc.mime_type,
                            raw_text=old_doc.raw_text,
                            confidence_score=old_doc.confidence_score,
                            ocr_provider=old_doc.ocr_provider,
                            processing_time_seconds=float(old_doc.processing_time) if old_doc.processing_time else None,
                            created_at=old_doc.created_at,
                            updated_at=old_doc.updated_at,
                            status="processed" if old_doc.raw_text else "uploaded"
                        )
                        
                        # Migrar datos extraídos si existen
                        if old_doc.extracted_data:
                            new_doc.set_extracted_data(old_doc.extracted_data)
                        
                        db.add(new_doc)
                        migrated_count += 1
                        
                    except Exception as e:
                        logger.warning(f"⚠️ Error migrando documento {old_doc.id}: {e}")
                        continue
                
                db.commit()
                logger.info(f"✅ Migrados {migrated_count} documentos")
            
        except Exception as e:
            logger.warning(f"⚠️ No se pudieron migrar documentos del esquema anterior: {e}")
        
        db.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Error migrando documentos: {e}")
        return False


def create_directories():
    """Crear directorios necesarios"""
    logger.info("🔄 Creando directorios necesarios...")
    
    try:
        directories = [
            "uploads",
            "outputs", 
            "logs",
            "data",
            "backups"
        ]
        
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
            logger.info(f"✅ Directorio creado: {directory}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creando directorios: {e}")
        return False


def update_configuration():
    """Actualizar archivos de configuración"""
    logger.info("🔄 Actualizando configuración...")
    
    try:
        # Crear archivo de configuración optimizado si no existe
        config_file = Path("config_optimized.env")
        if not config_file.exists():
            logger.info("✅ Archivo de configuración optimizado ya existe")
        else:
            logger.info("✅ Archivo de configuración optimizado creado")
        
        # Crear archivo .env si no existe
        env_file = Path(".env")
        if not env_file.exists():
            import shutil
            shutil.copy2("config_optimized.env", ".env")
            logger.info("✅ Archivo .env creado desde configuración optimizada")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error actualizando configuración: {e}")
        return False


def verify_migration():
    """Verificar que la migración fue exitosa"""
    logger.info("🔄 Verificando migración...")
    
    try:
        # Inicializar base de datos
        import asyncio
        asyncio.run(init_database())
        
        # Crear sesión
        SessionLocal = create_session_factory()
        db = SessionLocal()
        
        # Verificar que las tablas existen
        from sqlalchemy import inspect
        inspector = inspect(create_database_engine())
        tables = inspector.get_table_names()
        
        expected_tables = ['documents', 'users', 'organizations']
        missing_tables = [table for table in expected_tables if table not in tables]
        
        if missing_tables:
            logger.error(f"❌ Tablas faltantes: {missing_tables}")
            return False
        
        # Verificar documentos
        document_count = db.query(Document).count()
        logger.info(f"📊 Documentos en nueva base de datos: {document_count}")
        
        # Verificar configuración
        settings = get_settings()
        logger.info(f"📊 Configuración cargada: {settings.name} v{settings.version}")
        
        db.close()
        logger.info("✅ Migración verificada exitosamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error verificando migración: {e}")
        return False


def main():
    """Función principal de migración"""
    logger.info("🚀 Iniciando migración al sistema optimizado...")
    
    steps = [
        ("Backup de datos existentes", backup_existing_data),
        ("Creación de directorios", create_directories),
        ("Actualización de configuración", update_configuration),
        ("Migración de esquema de base de datos", migrate_database_schema),
        ("Migración de documentos existentes", migrate_existing_documents),
        ("Verificación de migración", verify_migration),
    ]
    
    success_count = 0
    total_steps = len(steps)
    
    for step_name, step_function in steps:
        logger.info(f"\n📋 {step_name}...")
        try:
            if step_function():
                success_count += 1
                logger.info(f"✅ {step_name} completado")
            else:
                logger.error(f"❌ {step_name} falló")
        except Exception as e:
            logger.error(f"❌ {step_name} falló con error: {e}")
    
    logger.info(f"\n🎉 Migración completada: {success_count}/{total_steps} pasos exitosos")
    
    if success_count == total_steps:
        logger.info("🎉 ¡Migración exitosa! El sistema optimizado está listo para usar.")
        logger.info("📖 Para iniciar el servidor: python src/app/main.py")
        logger.info("📖 Para usar Docker: docker-compose up -d")
    else:
        logger.error("❌ Migración incompleta. Revisar logs para más detalles.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
