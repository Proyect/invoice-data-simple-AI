#!/usr/bin/env python3
"""
Test de Infraestructura
========================

Tests de base de datos, Redis, conexiones y configuración.
"""
import sys
import os
import time
import psycopg2
import redis
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app.core.database import (
    create_database_engine,
    get_db,
    is_database_healthy,
    is_redis_healthy,
    get_redis
)
from app.core.environment import get_settings
from app.models.document import Document
from sqlalchemy.orm import Session


@dataclass
class InfrastructureTestResult:
    """Resultado de test de infraestructura"""
    component: str
    success: bool
    response_time_ms: Optional[float] = None
    error: Optional[str] = None
    details: Optional[Dict] = None


class InfrastructureTester:
    """Tester para infraestructura"""
    
    def __init__(self):
        self.settings = get_settings()
        self.test_results: list[InfrastructureTestResult] = []
    
    def test_postgresql_connection(self) -> InfrastructureTestResult:
        """Testear conexión a PostgreSQL"""
        print("🗄️  Testeando conexión a PostgreSQL...")
        
        start_time = time.time()
        
        try:
            database_url = self.settings.database.url
            
            if "postgresql" not in database_url.lower():
                return InfrastructureTestResult(
                    component="PostgreSQL",
                    success=False,
                    error="No se está usando PostgreSQL (usando SQLite o otro)"
                )
            
            # Extraer información de conexión
            conn = psycopg2.connect(database_url)
            cursor = conn.cursor()
            
            # Test básico
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            
            # Test de tabla documents
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'documents'
                );
            """)
            table_exists = cursor.fetchone()[0]
            
            # Obtener información de la base de datos
            cursor.execute("SELECT current_database(), current_user;")
            db_info = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            elapsed_ms = (time.time() - start_time) * 1000
            
            details = {
                "version": version.split(',')[0] if version else "Unknown",
                "database": db_info[0] if db_info else "Unknown",
                "user": db_info[1] if db_info else "Unknown",
                "documents_table_exists": table_exists
            }
            
            result = InfrastructureTestResult(
                component="PostgreSQL",
                success=True,
                response_time_ms=elapsed_ms,
                details=details
            )
            
            print(f"   ✅ PostgreSQL conectado ({elapsed_ms:.0f}ms)")
            print(f"      Base de datos: {details['database']}")
            print(f"      Tabla 'documents': {'Existe' if table_exists else 'No existe'}")
            
        except psycopg2.OperationalError as e:
            result = InfrastructureTestResult(
                component="PostgreSQL",
                success=False,
                error=f"Error de conexión: {str(e)}"
            )
            print(f"   ❌ Error conectando a PostgreSQL: {e}")
        except Exception as e:
            result = InfrastructureTestResult(
                component="PostgreSQL",
                success=False,
                error=f"Error: {str(e)}"
            )
            print(f"   ❌ Error: {e}")
        
        self.test_results.append(result)
        return result
    
    def test_sqlite_fallback(self) -> InfrastructureTestResult:
        """Testear fallback a SQLite"""
        print("🗄️  Testeando fallback a SQLite...")
        
        start_time = time.time()
        
        try:
            database_url = self.settings.database.url_fallback
            
            if "sqlite" not in database_url.lower():
                return InfrastructureTestResult(
                    component="SQLite",
                    success=False,
                    error="SQLite no configurado como fallback"
                )
            
            # Verificar que el archivo existe o puede crearse
            from sqlalchemy import create_engine
            engine = create_engine(database_url)
            
            # Test de conexión
            with engine.connect() as conn:
                result_query = conn.execute("SELECT 1")
                result_query.fetchone()
            
            elapsed_ms = (time.time() - start_time) * 1000
            
            result = InfrastructureTestResult(
                component="SQLite",
                success=True,
                response_time_ms=elapsed_ms,
                details={"url": database_url}
            )
            
            print(f"   ✅ SQLite disponible ({elapsed_ms:.0f}ms)")
            
        except Exception as e:
            result = InfrastructureTestResult(
                component="SQLite",
                success=False,
                error=f"Error: {str(e)}"
            )
            print(f"   ❌ Error con SQLite: {e}")
        
        self.test_results.append(result)
        return result
    
    def test_database_health_check(self) -> InfrastructureTestResult:
        """Testear health check de base de datos"""
        print("🏥 Testeando health check de base de datos...")
        
        start_time = time.time()
        
        try:
            is_healthy = is_database_healthy()
            elapsed_ms = (time.time() - start_time) * 1000
            
            result = InfrastructureTestResult(
                component="Database Health Check",
                success=is_healthy,
                response_time_ms=elapsed_ms,
                details={"healthy": is_healthy}
            )
            
            if is_healthy:
                print(f"   ✅ Base de datos saludable ({elapsed_ms:.0f}ms)")
            else:
                print(f"   ❌ Base de datos no saludable ({elapsed_ms:.0f}ms)")
                result.error = "Health check retornó False"
            
        except Exception as e:
            result = InfrastructureTestResult(
                component="Database Health Check",
                success=False,
                error=f"Error: {str(e)}"
            )
            print(f"   ❌ Error en health check: {e}")
        
        self.test_results.append(result)
        return result
    
    def test_database_crud(self) -> InfrastructureTestResult:
        """Testear operaciones CRUD en base de datos"""
        print("📝 Testeando operaciones CRUD...")
        
        start_time = time.time()
        
        try:
            # Obtener sesión de base de datos
            db_gen = get_db()
            db: Session = next(db_gen)
            
            test_doc_id = None
            
            try:
                # CREATE
                test_document = Document(
                    filename="test_crud.pdf",
                    original_filename="test_crud.pdf",
                    file_path="/test/test_crud.pdf",
                    status="pending",
                    priority=5,
                    language="es",
                    is_deleted=False
                )
                db.add(test_document)
                db.commit()
                db.refresh(test_document)
                test_doc_id = test_document.id
                
                # READ
                retrieved_doc = db.query(Document).filter(Document.id == test_doc_id).first()
                if not retrieved_doc:
                    raise Exception("No se pudo leer el documento creado")
                
                # UPDATE
                retrieved_doc.status = "processed"
                db.commit()
                db.refresh(retrieved_doc)
                
                if retrieved_doc.status != "processed":
                    raise Exception("No se pudo actualizar el documento")
                
                # DELETE (soft delete)
                retrieved_doc.is_deleted = True
                db.commit()
                
                # Verificar soft delete
                active_doc = db.query(Document).filter(
                    Document.id == test_doc_id,
                    Document.is_deleted == False
                ).first()
                
                if active_doc:
                    raise Exception("Soft delete no funcionó correctamente")
                
                # Limpiar - eliminar permanentemente
                db.query(Document).filter(Document.id == test_doc_id).delete()
                db.commit()
                
                elapsed_ms = (time.time() - start_time) * 1000
                
                result = InfrastructureTestResult(
                    component="Database CRUD",
                    success=True,
                    response_time_ms=elapsed_ms,
                    details={
                        "create": True,
                        "read": True,
                        "update": True,
                        "delete": True
                    }
                )
                
                print(f"   ✅ Operaciones CRUD exitosas ({elapsed_ms:.0f}ms)")
                
            except Exception as e:
                # Limpiar en caso de error
                if test_doc_id:
                    try:
                        db.query(Document).filter(Document.id == test_doc_id).delete()
                        db.commit()
                    except:
                        pass
                raise e
            finally:
                db.close()
                
        except Exception as e:
            result = InfrastructureTestResult(
                component="Database CRUD",
                success=False,
                error=f"Error: {str(e)}"
            )
            print(f"   ❌ Error en operaciones CRUD: {e}")
        
        self.test_results.append(result)
        return result
    
    def test_redis_connection(self) -> InfrastructureTestResult:
        """Testear conexión a Redis"""
        print("🔴 Testeando conexión a Redis...")
        
        start_time = time.time()
        
        try:
            redis_client = get_redis()
            
            if not redis_client:
                return InfrastructureTestResult(
                    component="Redis",
                    success=False,
                    error="Redis client no disponible"
                )
            
            # Test básico
            test_key = f"test_{int(time.time())}"
            test_value = "test_value"
            
            redis_client.set(test_key, test_value, ex=10)
            retrieved_value = redis_client.get(test_key)
            
            if retrieved_value and retrieved_value.decode() == test_value:
                redis_client.delete(test_key)
                
                # Obtener información de Redis
                info = redis_client.info()
                
                elapsed_ms = (time.time() - start_time) * 1000
                
                details = {
                    "version": info.get("redis_version", "Unknown"),
                    "connected_clients": info.get("connected_clients", 0),
                    "used_memory_human": info.get("used_memory_human", "Unknown")
                }
                
                result = InfrastructureTestResult(
                    component="Redis",
                    success=True,
                    response_time_ms=elapsed_ms,
                    details=details
                )
                
                print(f"   ✅ Redis conectado ({elapsed_ms:.0f}ms)")
                print(f"      Versión: {details['version']}")
                print(f"      Clientes conectados: {details['connected_clients']}")
            else:
                result = InfrastructureTestResult(
                    component="Redis",
                    success=False,
                    error="No se pudo leer el valor escrito"
                )
                print(f"   ❌ Error: No se pudo leer el valor escrito")
                
        except redis.ConnectionError as e:
            result = InfrastructureTestResult(
                component="Redis",
                success=False,
                error=f"Error de conexión: {str(e)}"
            )
            print(f"   ❌ Error conectando a Redis: {e}")
        except Exception as e:
            result = InfrastructureTestResult(
                component="Redis",
                success=False,
                error=f"Error: {str(e)}"
            )
            print(f"   ❌ Error: {e}")
        
        self.test_results.append(result)
        return result
    
    def test_redis_health_check(self) -> InfrastructureTestResult:
        """Testear health check de Redis"""
        print("🏥 Testeando health check de Redis...")
        
        start_time = time.time()
        
        try:
            is_healthy = is_redis_healthy()
            elapsed_ms = (time.time() - start_time) * 1000
            
            result = InfrastructureTestResult(
                component="Redis Health Check",
                success=is_healthy,
                response_time_ms=elapsed_ms,
                details={"healthy": is_healthy}
            )
            
            if is_healthy:
                print(f"   ✅ Redis saludable ({elapsed_ms:.0f}ms)")
            else:
                print(f"   ⚠️  Redis no saludable ({elapsed_ms:.0f}ms) - puede ser opcional")
                # Redis es opcional, no marcamos como error
                result.success = True
            
        except Exception as e:
            result = InfrastructureTestResult(
                component="Redis Health Check",
                success=True,  # Redis es opcional
                error=f"Error: {str(e)}"
            )
            print(f"   ⚠️  Error en health check de Redis: {e} (opcional)")
        
        self.test_results.append(result)
        return result
    
    def test_database_migrations(self) -> InfrastructureTestResult:
        """Testear migraciones de base de datos"""
        print("🔄 Testeando migraciones de base de datos...")
        
        start_time = time.time()
        
        try:
            from alembic.config import Config
            from alembic import command
            from alembic.script import ScriptDirectory
            from alembic.runtime.migration import MigrationContext
            
            # Obtener configuración de Alembic
            alembic_cfg = Config("alembic.ini")
            script = ScriptDirectory.from_config(alembic_cfg)
            
            # Obtener versión actual
            db_gen = get_db()
            db: Session = next(db_gen)
            
            try:
                context = MigrationContext.configure(db.connection())
                current_rev = context.get_current_revision()
                head_rev = script.get_current_head()
                
                elapsed_ms = (time.time() - start_time) * 1000
                
                details = {
                    "current_revision": current_rev,
                    "head_revision": head_rev,
                    "up_to_date": current_rev == head_rev
                }
                
                if current_rev == head_rev:
                    result = InfrastructureTestResult(
                        component="Database Migrations",
                        success=True,
                        response_time_ms=elapsed_ms,
                        details=details
                    )
                    print(f"   ✅ Migraciones al día ({elapsed_ms:.0f}ms)")
                    print(f"      Revisión actual: {current_rev}")
                else:
                    result = InfrastructureTestResult(
                        component="Database Migrations",
                        success=False,
                        response_time_ms=elapsed_ms,
                        error=f"Migraciones desactualizadas. Actual: {current_rev}, Head: {head_rev}",
                        details=details
                    )
                    print(f"   ⚠️  Migraciones desactualizadas")
                    print(f"      Actual: {current_rev}, Head: {head_rev}")
                
            finally:
                db.close()
                
        except Exception as e:
            result = InfrastructureTestResult(
                component="Database Migrations",
                success=False,
                error=f"Error: {str(e)}"
            )
            print(f"   ❌ Error verificando migraciones: {e}")
        
        self.test_results.append(result)
        return result
    
    def run_all_tests(self):
        """Ejecutar todos los tests de infraestructura"""
        print("🚀 Iniciando tests de infraestructura...")
        print("=" * 60)
        print()
        
        self.test_postgresql_connection()
        self.test_sqlite_fallback()
        self.test_database_health_check()
        self.test_database_crud()
        self.test_redis_connection()
        self.test_redis_health_check()
        self.test_database_migrations()
        
        print()
    
    def print_summary(self):
        """Imprimir resumen de resultados"""
        print("=" * 60)
        print("📊 RESUMEN DE TESTS DE INFRAESTRUCTURA")
        print("=" * 60)
        
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r.success)
        failed = total - passed
        
        print(f"Total de tests: {total}")
        print(f"Pasaron: {passed}")
        print(f"Fallaron: {failed}")
        print(f"Tasa de éxito: {(passed/total*100):.1f}%" if total > 0 else "N/A")
        print()
        
        if failed > 0:
            print("❌ Tests que fallaron:")
            for result in self.test_results:
                if not result.success:
                    print(f"   - {result.component}: {result.error}")
            print()
        
        return failed == 0


def main():
    """Función principal"""
    tester = InfrastructureTester()
    tester.run_all_tests()
    all_passed = tester.print_summary()
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())









































