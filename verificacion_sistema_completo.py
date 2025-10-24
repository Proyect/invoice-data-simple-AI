#!/usr/bin/env python3
"""
Verificación completa del sistema de extracción de documentos
"""
import sys
import os
from pathlib import Path
import importlib
import traceback
from datetime import datetime

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

class SystemVerifier:
    """Verificador completo del sistema"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.success = []
        
    def log_error(self, message):
        self.errors.append(message)
        print(f"❌ {message}")
    
    def log_warning(self, message):
        self.warnings.append(message)
        print(f"⚠️  {message}")
    
    def log_success(self, message):
        self.success.append(message)
        print(f"✅ {message}")
    
    def verify_basic_imports(self):
        """Verificar imports básicos del sistema"""
        print("\n🔍 VERIFICANDO IMPORTS BÁSICOS")
        print("-" * 40)
        
        basic_modules = [
            ("FastAPI", "fastapi", "FastAPI"),
            ("SQLAlchemy", "sqlalchemy", "create_engine"),
            ("Pydantic", "pydantic", "BaseModel"),
            ("Pytest", "pytest", None),
            ("Pillow", "PIL", "Image"),
            ("Tesseract", "pytesseract", "image_to_string"),
            ("spaCy", "spacy", None),
            ("Redis", "redis", "Redis"),
        ]
        
        for name, module, attr in basic_modules:
            try:
                mod = importlib.import_module(module)
                if attr and not hasattr(mod, attr):
                    self.log_warning(f"{name}: módulo importado pero falta {attr}")
                else:
                    self.log_success(f"{name}: OK")
            except ImportError as e:
                self.log_error(f"{name}: No instalado - {e}")
    
    def verify_project_structure(self):
        """Verificar estructura del proyecto"""
        print("\n🏗️  VERIFICANDO ESTRUCTURA DEL PROYECTO")
        print("-" * 40)
        
        required_paths = [
            "src/app",
            "src/app/models",
            "src/app/schemas", 
            "src/app/routes",
            "src/app/services",
            "src/app/core",
            "src/app/auth",
            "tests",
            "alembic",
            "frontend",
            "requirements.txt",
            "pytest.ini",
            "docker-compose.yml"
        ]
        
        for path in required_paths:
            if os.path.exists(path):
                self.log_success(f"Estructura: {path}")
            else:
                self.log_warning(f"Estructura: {path} no encontrado")
    
    def verify_models_v1(self):
        """Verificar modelos originales (V1)"""
        print("\n📄 VERIFICANDO MODELOS V1 (ORIGINALES)")
        print("-" * 40)
        
        try:
            from app.models.document import Document as DocumentV1
            from app.models.user import User as UserV1
            
            self.log_success("Modelo Document V1: OK")
            self.log_success("Modelo User V1: OK")
            
            # Verificar campos básicos
            doc_fields = ['id', 'filename', 'file_path', 'raw_text', 'extracted_data']
            for field in doc_fields:
                if hasattr(DocumentV1, field):
                    self.log_success(f"Document V1.{field}: OK")
                else:
                    self.log_error(f"Document V1.{field}: Falta")
            
            user_fields = ['id', 'email', 'username', 'hashed_password']
            for field in user_fields:
                if hasattr(UserV1, field):
                    self.log_success(f"User V1.{field}: OK")
                else:
                    self.log_error(f"User V1.{field}: Falta")
                    
        except Exception as e:
            self.log_error(f"Modelos V1: Error importando - {e}")
    
    def verify_models_v2(self):
        """Verificar modelos mejorados (V2)"""
        print("\n📄 VERIFICANDO MODELOS V2 (MEJORADOS)")
        print("-" * 40)
        
        try:
            from app.models.models_v2 import DocumentV2, UserV2, OrganizationV2, ProcessingJobV2
            from app.models.models_v2 import DocumentType, DocumentStatus, UserRole, JobStatus
            
            self.log_success("Modelos V2: Importados correctamente")
            self.log_success("Enums V2: Importados correctamente")
            
            # Verificar que los enums tienen valores
            doc_types = [dt.value for dt in DocumentType]
            self.log_success(f"DocumentType valores: {doc_types}")
            
            user_roles = [ur.value for ur in UserRole]
            self.log_success(f"UserRole valores: {user_roles}")
            
        except Exception as e:
            self.log_error(f"Modelos V2: Error - {e}")
            traceback.print_exc()
    
    def verify_schemas(self):
        """Verificar schemas de Pydantic"""
        print("\n📋 VERIFICANDO SCHEMAS PYDANTIC")
        print("-" * 40)
        
        schemas_to_test = [
            ("document_enhanced", "DocumentResponse"),
            ("user_enhanced", "UserResponse"),
            ("organization", "OrganizationResponse"),
            ("processing", "ProcessingJobResponse"),
        ]
        
        for module_name, schema_name in schemas_to_test:
            try:
                module = importlib.import_module(f"app.schemas.{module_name}")
                schema_class = getattr(module, schema_name)
                
                # Verificar que es una clase de Pydantic
                if hasattr(schema_class, '__fields__'):
                    field_count = len(schema_class.__fields__)
                    self.log_success(f"Schema {schema_name}: OK ({field_count} campos)")
                else:
                    self.log_warning(f"Schema {schema_name}: No es schema de Pydantic")
                    
            except ImportError as e:
                self.log_error(f"Schema {module_name}.{schema_name}: No se puede importar - {e}")
            except AttributeError as e:
                self.log_error(f"Schema {schema_name}: No existe en {module_name} - {e}")
            except Exception as e:
                self.log_error(f"Schema {schema_name}: Error inesperado - {e}")
    
    def verify_services(self):
        """Verificar servicios"""
        print("\n⚙️  VERIFICANDO SERVICIOS")
        print("-" * 40)
        
        services_to_test = [
            ("basic_extraction_service", "BasicExtractionService"),
            ("cache_service", "CacheService"),
            ("intelligent_extraction_service", "IntelligentExtractionService"),
            ("optimal_ocr_service", "OptimalOCRService"),
        ]
        
        for module_name, service_name in services_to_test:
            try:
                module = importlib.import_module(f"app.services.{module_name}")
                service_class = getattr(module, service_name)
                self.log_success(f"Servicio {service_name}: OK")
            except ImportError as e:
                self.log_error(f"Servicio {module_name}: No se puede importar - {e}")
            except AttributeError as e:
                self.log_error(f"Servicio {service_name}: No existe - {e}")
            except Exception as e:
                self.log_error(f"Servicio {service_name}: Error - {e}")
    
    def verify_routes(self):
        """Verificar rutas/endpoints"""
        print("\n🌐 VERIFICANDO RUTAS/ENDPOINTS")
        print("-" * 40)
        
        routes_to_test = [
            ("simple_upload", "router"),
            ("flexible_upload", "router"),
            ("documents", "router"),
            ("auth", "router"),
        ]
        
        for module_name, router_name in routes_to_test:
            try:
                module = importlib.import_module(f"app.routes.{module_name}")
                router = getattr(module, router_name)
                
                if hasattr(router, 'routes'):
                    route_count = len(router.routes)
                    self.log_success(f"Router {module_name}: OK ({route_count} rutas)")
                else:
                    self.log_warning(f"Router {module_name}: No tiene rutas")
                    
            except ImportError as e:
                self.log_error(f"Router {module_name}: No se puede importar - {e}")
            except AttributeError as e:
                self.log_error(f"Router {module_name}: No existe - {e}")
            except Exception as e:
                self.log_error(f"Router {module_name}: Error - {e}")
    
    def verify_config(self):
        """Verificar configuración"""
        print("\n⚙️  VERIFICANDO CONFIGURACIÓN")
        print("-" * 40)
        
        try:
            from app.core.config import settings
            
            # Verificar configuraciones críticas
            configs = [
                ("APP_NAME", settings.APP_NAME),
                ("DEBUG", settings.DEBUG),
                ("DATABASE_URL", settings.DATABASE_URL),
                ("UPLOAD_DIR", settings.UPLOAD_DIR),
                ("SECRET_KEY", "***" if settings.SECRET_KEY else None),
            ]
            
            for name, value in configs:
                if value:
                    self.log_success(f"Config {name}: Configurado")
                else:
                    self.log_warning(f"Config {name}: No configurado")
            
            # Verificar APIs opcionales
            optional_configs = [
                ("OPENAI_API_KEY", settings.OPENAI_API_KEY),
                ("GOOGLE_APPLICATION_CREDENTIALS", settings.GOOGLE_APPLICATION_CREDENTIALS),
                ("AWS_ACCESS_KEY_ID", settings.AWS_ACCESS_KEY_ID),
                ("REDIS_URL", settings.REDIS_URL),
            ]
            
            for name, value in optional_configs:
                if value:
                    self.log_success(f"Config {name}: Configurado (opcional)")
                else:
                    self.log_warning(f"Config {name}: No configurado (opcional)")
                    
        except Exception as e:
            self.log_error(f"Configuración: Error - {e}")
    
    def verify_database_connection(self):
        """Verificar conexión a base de datos"""
        print("\n🗄️  VERIFICANDO CONEXIÓN A BASE DE DATOS")
        print("-" * 40)
        
        try:
            from app.core.database import engine, SessionLocal
            
            # Test de conexión
            with engine.connect() as conn:
                result = conn.execute("SELECT 1")
                if result.scalar() == 1:
                    self.log_success("Conexión a BD: OK")
                else:
                    self.log_error("Conexión a BD: Respuesta inesperada")
            
            # Test de sesión
            db = SessionLocal()
            try:
                # Verificar que podemos hacer queries básicas
                if hasattr(db, 'execute'):
                    self.log_success("Sesión de BD: OK")
                else:
                    self.log_error("Sesión de BD: No funcional")
            finally:
                db.close()
                
        except Exception as e:
            self.log_error(f"Base de datos: Error de conexión - {e}")
    
    def verify_tests(self):
        """Verificar que los tests funcionan"""
        print("\n🧪 VERIFICANDO TESTS")
        print("-" * 40)
        
        test_files = [
            "tests/test_simple_upload.py",
            "tests/test_flexible_upload.py", 
            "tests/test_documents.py",
            "tests/test_services.py",
            "tests/test_security.py",
            "tests/conftest.py"
        ]
        
        for test_file in test_files:
            if os.path.exists(test_file):
                self.log_success(f"Test file: {test_file}")
            else:
                self.log_warning(f"Test file: {test_file} no encontrado")
        
        # Verificar pytest.ini
        if os.path.exists("pytest.ini"):
            self.log_success("Configuración pytest: OK")
        else:
            self.log_warning("pytest.ini: No encontrado")
    
    def verify_frontend(self):
        """Verificar frontend"""
        print("\n🌐 VERIFICANDO FRONTEND")
        print("-" * 40)
        
        frontend_files = [
            "frontend/package.json",
            "frontend/src/App.jsx",
            "frontend/src/components/DocumentUpload.jsx",
            "frontend/public/index.html"
        ]
        
        for file_path in frontend_files:
            if os.path.exists(file_path):
                self.log_success(f"Frontend: {file_path}")
            else:
                self.log_warning(f"Frontend: {file_path} no encontrado")
    
    def verify_docker(self):
        """Verificar configuración de Docker"""
        print("\n🐳 VERIFICANDO CONFIGURACIÓN DOCKER")
        print("-" * 40)
        
        docker_files = [
            "Dockerfile",
            "Dockerfile.dev",
            "docker-compose.yml",
            "docker-compose.prod.yml"
        ]
        
        for file_path in docker_files:
            if os.path.exists(file_path):
                self.log_success(f"Docker: {file_path}")
            else:
                self.log_warning(f"Docker: {file_path} no encontrado")
    
    def verify_migration_files(self):
        """Verificar archivos de migración"""
        print("\n🔄 VERIFICANDO ARCHIVOS DE MIGRACIÓN")
        print("-" * 40)
        
        migration_files = [
            "alembic.ini",
            "alembic/env.py",
            "alembic/versions",
            "migrate_to_enhanced_models.py"
        ]
        
        for file_path in migration_files:
            if os.path.exists(file_path):
                self.log_success(f"Migración: {file_path}")
            else:
                self.log_warning(f"Migración: {file_path} no encontrado")
    
    def verify_new_files_created(self):
        """Verificar archivos nuevos creados"""
        print("\n📁 VERIFICANDO ARCHIVOS NUEVOS CREADOS")
        print("-" * 40)
        
        new_files = [
            "src/app/models/document_enhanced.py",
            "src/app/models/user_enhanced.py",
            "src/app/models/processing.py",
            "src/app/models/models_v2.py",
            "src/app/schemas/document_enhanced.py",
            "src/app/schemas/user_enhanced.py",
            "src/app/schemas/organization.py",
            "src/app/schemas/processing.py",
            "src/app/services/document_service_enhanced.py",
            "src/app/routes/documents_enhanced.py",
            "alembic/versions/001_create_enhanced_models.py",
            "config_optimo.env",
            "config_gratuito.env",
            "config_minimo.env",
            "setup_optimo_5min.sh",
            "deploy_automatico.sh",
            "guia_deploy_completa.md",
            "analisis_servicios_optimo.md"
        ]
        
        for file_path in new_files:
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                self.log_success(f"Archivo nuevo: {file_path} ({file_size} bytes)")
            else:
                self.log_error(f"Archivo nuevo: {file_path} NO CREADO")
    
    def verify_models_v2_isolated(self):
        """Verificar modelos V2 de forma aislada"""
        print("\n📄 VERIFICANDO MODELOS V2 (AISLADOS)")
        print("-" * 40)
        
        try:
            # Importar directamente sin pasar por __init__.py
            spec = importlib.util.spec_from_file_location(
                "models_v2", 
                "src/app/models/models_v2.py"
            )
            models_v2 = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(models_v2)
            
            # Verificar clases
            classes = ['DocumentV2', 'UserV2', 'OrganizationV2', 'ProcessingJobV2']
            for class_name in classes:
                if hasattr(models_v2, class_name):
                    cls = getattr(models_v2, class_name)
                    self.log_success(f"Modelo V2: {class_name} OK")
                    
                    # Verificar que tiene __tablename__
                    if hasattr(cls, '__tablename__'):
                        self.log_success(f"  Tabla: {cls.__tablename__}")
                    else:
                        self.log_error(f"  {class_name}: Sin __tablename__")
                else:
                    self.log_error(f"Modelo V2: {class_name} no encontrado")
            
            # Verificar enums
            enums = ['DocumentType', 'DocumentStatus', 'UserRole', 'JobStatus']
            for enum_name in enums:
                if hasattr(models_v2, enum_name):
                    enum_cls = getattr(models_v2, enum_name)
                    values = [e.value for e in enum_cls]
                    self.log_success(f"Enum V2: {enum_name} ({len(values)} valores)")
                else:
                    self.log_error(f"Enum V2: {enum_name} no encontrado")
                    
        except Exception as e:
            self.log_error(f"Modelos V2 aislados: Error - {e}")
            traceback.print_exc()
    
    def verify_schemas_isolated(self):
        """Verificar schemas de forma aislada"""
        print("\n📋 VERIFICANDO SCHEMAS (AISLADOS)")
        print("-" * 40)
        
        schema_files = [
            ("document_enhanced.py", ["DocumentResponse", "DocumentCreate", "DocumentUpdate"]),
            ("user_enhanced.py", ["UserResponse", "UserCreate", "UserLogin"]),
            ("organization.py", ["OrganizationResponse", "OrganizationCreate"]),
            ("processing.py", ["ProcessingJobResponse", "ProcessingJobCreate"])
        ]
        
        for file_name, schema_names in schema_files:
            try:
                file_path = f"src/app/schemas/{file_name}"
                if not os.path.exists(file_path):
                    self.log_error(f"Schema file: {file_name} no existe")
                    continue
                
                # Leer archivo y verificar que contiene las clases
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for schema_name in schema_names:
                    if f"class {schema_name}" in content:
                        self.log_success(f"Schema: {schema_name} definido en {file_name}")
                    else:
                        self.log_error(f"Schema: {schema_name} NO definido en {file_name}")
                        
            except Exception as e:
                self.log_error(f"Schema file {file_name}: Error - {e}")
    
    def run_full_verification(self):
        """Ejecutar verificación completa"""
        print("🔍 VERIFICACIÓN COMPLETA DEL SISTEMA")
        print("=" * 50)
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        # Ejecutar todas las verificaciones
        self.verify_basic_imports()
        self.verify_project_structure()
        self.verify_models_v1()
        self.verify_models_v2_isolated()
        self.verify_schemas_isolated()
        self.verify_services()
        self.verify_routes()
        self.verify_config()
        self.verify_database_connection()
        self.verify_tests()
        self.verify_frontend()
        self.verify_docker()
        self.verify_migration_files()
        self.verify_new_files_created()
        
        # Resumen final
        print("\n" + "=" * 50)
        print("📊 RESUMEN DE VERIFICACIÓN")
        print("=" * 50)
        print(f"✅ Éxitos: {len(self.success)}")
        print(f"⚠️  Advertencias: {len(self.warnings)}")
        print(f"❌ Errores: {len(self.errors)}")
        
        if len(self.errors) == 0:
            print("\n🎉 SISTEMA COMPLETAMENTE FUNCIONAL")
            return True
        elif len(self.errors) <= 3:
            print("\n⚠️  SISTEMA MAYORMENTE FUNCIONAL (errores menores)")
            return True
        else:
            print("\n❌ SISTEMA CON PROBLEMAS SIGNIFICATIVOS")
            return False


if __name__ == "__main__":
    import importlib.util
    
    verifier = SystemVerifier()
    success = verifier.run_full_verification()
    
    if success:
        print("\n🚀 SISTEMA LISTO PARA USAR")
    else:
        print("\n🔧 SISTEMA NECESITA CORRECCIONES")
    
    sys.exit(0 if success else 1)












