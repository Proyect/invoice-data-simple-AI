#!/usr/bin/env python3
"""
Script de migración segura de modelos básicos a modelos mejorados
"""
import sys
import os
from pathlib import Path
from datetime import datetime
import logging

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.core.database import Base

# Importar modelos antiguos y nuevos
from app.models.document import Document as DocumentOld
from app.models.user import User as UserOld
from app.models.document_enhanced import Document as DocumentNew, DocumentStatus, DocumentType
from app.models.user_enhanced import User as UserNew, UserRole, UserStatus, AuthProvider

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelMigrator:
    """Migrador de modelos con validación y rollback"""
    
    def __init__(self):
        self.engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(bind=self.engine)
        self.db = SessionLocal()
        
        self.migration_log = []
        self.backup_created = False
    
    def create_backup(self):
        """Crear backup antes de la migración"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"backup_before_migration_{timestamp}.sql"
            
            # Comando de backup (ajustar según tu DB)
            if "postgresql" in settings.DATABASE_URL:
                import subprocess
                result = subprocess.run([
                    "pg_dump", 
                    settings.DATABASE_URL,
                    "-f", backup_file
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    logger.info(f"✅ Backup creado: {backup_file}")
                    self.backup_created = True
                    return backup_file
                else:
                    logger.error(f"❌ Error creando backup: {result.stderr}")
                    return None
            else:
                # Para SQLite, simplemente copiar el archivo
                import shutil
                db_file = settings.DATABASE_URL.replace("sqlite:///", "")
                if os.path.exists(db_file):
                    shutil.copy2(db_file, f"{db_file}.backup_{timestamp}")
                    logger.info(f"✅ Backup SQLite creado: {db_file}.backup_{timestamp}")
                    self.backup_created = True
                    return f"{db_file}.backup_{timestamp}"
        
        except Exception as e:
            logger.error(f"❌ Error creando backup: {e}")
            return None
    
    def check_compatibility(self):
        """Verificar compatibilidad antes de migrar"""
        logger.info("🔍 Verificando compatibilidad...")
        
        try:
            # Verificar que las tablas antiguas existen
            result = self.db.execute(text("SELECT COUNT(*) FROM documents"))
            doc_count = result.scalar()
            logger.info(f"📄 Documentos existentes: {doc_count}")
            
            result = self.db.execute(text("SELECT COUNT(*) FROM users"))
            user_count = result.scalar()
            logger.info(f"👤 Usuarios existentes: {user_count}")
            
            # Verificar estructura de columnas
            if "postgresql" in settings.DATABASE_URL:
                # Verificar columnas en PostgreSQL
                result = self.db.execute(text("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'documents'
                """))
                columns = result.fetchall()
                logger.info(f"📋 Columnas en documents: {len(columns)}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error verificando compatibilidad: {e}")
            return False
    
    def migrate_documents(self):
        """Migrar documentos del modelo antiguo al nuevo"""
        logger.info("📄 Migrando documentos...")
        
        try:
            # Obtener documentos del modelo antiguo
            old_documents = self.db.query(DocumentOld).all()
            logger.info(f"📄 Documentos a migrar: {len(old_documents)}")
            
            migrated_count = 0
            error_count = 0
            
            for old_doc in old_documents:
                try:
                    # Verificar si ya existe en el nuevo modelo
                    existing = self.db.query(DocumentNew).filter(
                        DocumentNew.filename == old_doc.filename
                    ).first()
                    
                    if existing:
                        logger.info(f"⏭️  Documento ya migrado: {old_doc.id}")
                        continue
                    
                    # Crear documento en el nuevo modelo
                    new_doc = DocumentNew(
                        # Campos básicos
                        filename=old_doc.filename,
                        original_filename=old_doc.original_filename,
                        file_path=old_doc.file_path,
                        file_size=old_doc.file_size,
                        mime_type=old_doc.mime_type,
                        raw_text=old_doc.raw_text,
                        extracted_data=old_doc.extracted_data,
                        
                        # Mapear campos con valores por defecto
                        document_type=self._map_document_type(old_doc.extracted_data),
                        status=DocumentStatus.PROCESSED,  # Asumir que están procesados
                        priority=5,  # Prioridad normal
                        confidence_score=old_doc.confidence_score / 100.0 if old_doc.confidence_score else None,  # Convertir a 0-1
                        ocr_provider=self._map_ocr_provider(old_doc.ocr_provider),
                        ocr_cost=float(old_doc.ocr_cost) if old_doc.ocr_cost and old_doc.ocr_cost != "0.00" else 0.0,
                        language="es",
                        
                        # Timestamps
                        created_at=old_doc.created_at,
                        updated_at=old_doc.updated_at,
                        processed_at=old_doc.created_at,  # Asumir procesado al crear
                        
                        # Campos nuevos con valores por defecto
                        uuid=None,  # Se generará automáticamente
                        file_hash=None,  # Se calculará después si es necesario
                        quality_score=None,
                        extraction_method=ExtractionMethod.HYBRID,  # Valor por defecto
                        processing_time_seconds=None,
                        page_count=None,
                        word_count=len(old_doc.raw_text.split()) if old_doc.raw_text else None,
                        user_id=None,  # Se asignará después si hay relación
                        organization_id=None,  # Se asignará después
                        is_deleted=False
                    )
                    
                    self.db.add(new_doc)
                    self.db.flush()  # Para obtener el ID
                    
                    # Actualizar vector de búsqueda si es PostgreSQL
                    if "postgresql" in settings.DATABASE_URL:
                        new_doc.update_search_vector(self.db)
                    
                    migrated_count += 1
                    
                    if migrated_count % 100 == 0:
                        logger.info(f"📄 Migrados: {migrated_count}/{len(old_documents)}")
                        self.db.commit()  # Commit periódico
                
                except Exception as e:
                    logger.error(f"❌ Error migrando documento {old_doc.id}: {e}")
                    error_count += 1
                    self.db.rollback()
            
            # Commit final
            self.db.commit()
            
            logger.info(f"✅ Migración de documentos completada:")
            logger.info(f"   📄 Migrados: {migrated_count}")
            logger.info(f"   ❌ Errores: {error_count}")
            
            self.migration_log.append({
                "step": "migrate_documents",
                "migrated": migrated_count,
                "errors": error_count,
                "timestamp": datetime.now()
            })
            
            return migrated_count > 0
            
        except Exception as e:
            logger.error(f"❌ Error en migración de documentos: {e}")
            self.db.rollback()
            return False
    
    def migrate_users(self):
        """Migrar usuarios del modelo antiguo al nuevo"""
        logger.info("👤 Migrando usuarios...")
        
        try:
            # Obtener usuarios del modelo antiguo
            old_users = self.db.query(UserOld).all()
            logger.info(f"👤 Usuarios a migrar: {len(old_users)}")
            
            migrated_count = 0
            error_count = 0
            
            for old_user in old_users:
                try:
                    # Verificar si ya existe
                    existing = self.db.query(UserNew).filter(
                        UserNew.email == old_user.email
                    ).first()
                    
                    if existing:
                        logger.info(f"⏭️  Usuario ya migrado: {old_user.id}")
                        continue
                    
                    # Crear usuario en el nuevo modelo
                    new_user = UserNew(
                        # Campos básicos
                        email=old_user.email,
                        username=old_user.username,
                        full_name=old_user.full_name,
                        hashed_password=old_user.hashed_password,
                        
                        # Mapear campos
                        status=UserStatus.ACTIVE if old_user.is_active else UserStatus.INACTIVE,
                        role=UserRole.ADMIN if old_user.is_admin else UserRole.USER,
                        auth_provider=AuthProvider.LOCAL,
                        is_superuser=old_user.is_admin,
                        is_verified=old_user.is_verified,
                        
                        # Timestamps
                        created_at=old_user.created_at,
                        updated_at=old_user.updated_at,
                        last_login=old_user.last_login,
                        
                        # Campos nuevos con valores por defecto
                        uuid=None,  # Se generará automáticamente
                        first_name=None,
                        last_name=None,
                        phone=None,
                        avatar_url=None,
                        timezone="UTC",
                        language="es",
                        organization_id=None,
                        department=None,
                        job_title=None,
                        preferences=None,
                        permissions=None,
                        documents_processed=0,
                        total_processing_time=0.0,
                        is_deleted=False
                    )
                    
                    self.db.add(new_user)
                    migrated_count += 1
                
                except Exception as e:
                    logger.error(f"❌ Error migrando usuario {old_user.id}: {e}")
                    error_count += 1
                    self.db.rollback()
            
            # Commit final
            self.db.commit()
            
            logger.info(f"✅ Migración de usuarios completada:")
            logger.info(f"   👤 Migrados: {migrated_count}")
            logger.info(f"   ❌ Errores: {error_count}")
            
            self.migration_log.append({
                "step": "migrate_users",
                "migrated": migrated_count,
                "errors": error_count,
                "timestamp": datetime.now()
            })
            
            return migrated_count > 0
            
        except Exception as e:
            logger.error(f"❌ Error en migración de usuarios: {e}")
            self.db.rollback()
            return False
    
    def create_enhanced_tables(self):
        """Crear tablas de los modelos mejorados"""
        logger.info("🏗️  Creando tablas mejoradas...")
        
        try:
            # Importar todos los modelos mejorados
            from app.models.document_enhanced import Document, DocumentVersion, DocumentExtraction, DocumentTag, Organization
            from app.models.user_enhanced import User, UserSession, ApiKey, AuditLog
            from app.models.processing import ProcessingJob, ProcessingStep, ProcessingQueue, ProcessingWorker, ProcessingMetrics
            
            # Crear todas las tablas
            Base.metadata.create_all(bind=self.engine)
            
            logger.info("✅ Tablas mejoradas creadas correctamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creando tablas: {e}")
            return False
    
    def verify_migration(self):
        """Verificar que la migración fue exitosa"""
        logger.info("🔍 Verificando migración...")
        
        try:
            # Contar registros en tablas nuevas
            new_doc_count = self.db.query(DocumentNew).count()
            new_user_count = self.db.query(UserNew).count()
            
            logger.info(f"📄 Documentos en modelo nuevo: {new_doc_count}")
            logger.info(f"👤 Usuarios en modelo nuevo: {new_user_count}")
            
            # Verificar integridad básica
            docs_with_text = self.db.query(DocumentNew).filter(
                DocumentNew.raw_text.isnot(None)
            ).count()
            
            logger.info(f"📝 Documentos con texto: {docs_with_text}")
            
            return new_doc_count > 0 and new_user_count > 0
            
        except Exception as e:
            logger.error(f"❌ Error verificando migración: {e}")
            return False
    
    def _map_document_type(self, extracted_data):
        """Mapear tipo de documento desde datos extraídos"""
        if not extracted_data:
            return DocumentType.OTRO
        
        tipo = extracted_data.get("tipo_documento", "").lower()
        if "factura" in tipo:
            return DocumentType.FACTURA
        elif "recibo" in tipo:
            return DocumentType.RECIBO
        else:
            return DocumentType.OTRO
    
    def _map_ocr_provider(self, old_provider):
        """Mapear proveedor OCR"""
        if not old_provider:
            return None
        
        provider_map = {
            "tesseract": "tesseract",
            "google": "google_vision",
            "aws": "aws_textract"
        }
        
        from app.models.document_enhanced import OCRProvider
        provider_str = provider_map.get(old_provider.lower(), "tesseract")
        return OCRProvider(provider_str)
    
    def run_migration(self, create_backup=True, dry_run=False):
        """Ejecutar migración completa"""
        logger.info("🚀 INICIANDO MIGRACIÓN DE MODELOS")
        logger.info("=" * 50)
        
        if dry_run:
            logger.info("🧪 MODO DRY RUN - No se harán cambios permanentes")
        
        # Paso 1: Crear backup
        if create_backup and not dry_run:
            backup_file = self.create_backup()
            if not backup_file:
                logger.error("❌ No se pudo crear backup. Abortando migración.")
                return False
        
        # Paso 2: Verificar compatibilidad
        if not self.check_compatibility():
            logger.error("❌ Verificación de compatibilidad falló. Abortando.")
            return False
        
        if dry_run:
            logger.info("✅ Verificación de compatibilidad exitosa (DRY RUN)")
            return True
        
        # Paso 3: Crear tablas mejoradas
        if not self.create_enhanced_tables():
            logger.error("❌ Error creando tablas mejoradas. Abortando.")
            return False
        
        # Paso 4: Migrar datos
        users_migrated = self.migrate_users()
        docs_migrated = self.migrate_documents()
        
        if not (users_migrated or docs_migrated):
            logger.error("❌ No se pudo migrar ningún dato. Abortando.")
            return False
        
        # Paso 5: Verificar migración
        if not self.verify_migration():
            logger.error("❌ Verificación de migración falló.")
            return False
        
        # Paso 6: Log de migración
        self._save_migration_log()
        
        logger.info("🎉 MIGRACIÓN COMPLETADA EXITOSAMENTE")
        logger.info("=" * 50)
        logger.info("📋 Próximos pasos:")
        logger.info("   1. Verificar que la aplicación funciona correctamente")
        logger.info("   2. Actualizar imports en el código para usar modelos nuevos")
        logger.info("   3. Ejecutar tests para verificar funcionalidad")
        logger.info("   4. Considerar eliminar modelos antiguos después de validar")
        
        return True
    
    def _save_migration_log(self):
        """Guardar log de migración"""
        log_file = f"migration_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        import json
        with open(log_file, 'w') as f:
            json.dump({
                "migration_date": datetime.now().isoformat(),
                "database_url": settings.DATABASE_URL.split("@")[1] if "@" in settings.DATABASE_URL else "local",
                "backup_created": self.backup_created,
                "steps": self.migration_log,
                "success": True
            }, f, indent=2)
        
        logger.info(f"📋 Log de migración guardado: {log_file}")


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrar modelos básicos a modelos mejorados")
    parser.add_argument("--dry-run", action="store_true", help="Solo verificar, no hacer cambios")
    parser.add_argument("--no-backup", action="store_true", help="No crear backup")
    parser.add_argument("--force", action="store_true", help="Forzar migración sin confirmación")
    
    args = parser.parse_args()
    
    if not args.force and not args.dry_run:
        print("⚠️  ADVERTENCIA: Esta operación modificará la base de datos.")
        print("   Se recomienda crear un backup antes de continuar.")
        print("")
        response = input("¿Continuar con la migración? (y/N): ")
        if response.lower() != 'y':
            print("❌ Migración cancelada por el usuario.")
            return False
    
    migrator = ModelMigrator()
    
    success = migrator.run_migration(
        create_backup=not args.no_backup,
        dry_run=args.dry_run
    )
    
    if success:
        print("🎉 Migración completada exitosamente!")
        return True
    else:
        print("❌ Migración falló. Revisa los logs para más detalles.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


















