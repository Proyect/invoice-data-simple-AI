"""
Script de Inicio para el Sistema de Producción
==============================================

Script principal para iniciar el sistema completo de procesamiento de documentos.
Incluye verificaciones de sistema, inicialización de base de datos y configuración.

Uso:
    python start_production.py

Características:
- Verificación de dependencias
- Inicialización de base de datos
- Configuración de directorios
- Inicio del servidor FastAPI
- Logging completo
"""

import os
import sys
import logging
import subprocess
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/system.log')
    ]
)
logger = logging.getLogger(__name__)

def print_banner():
    """Mostrar banner del sistema"""
    banner = """
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║                    DOCUMENT EXTRACTOR API - PRODUCTION SYSTEM               ║
    ║                                                                              ║
    ║  Sistema Profesional de Procesamiento de Documentos con IA                  ║
    ║  Versión: 2.0.0                                                             ║
    ║  Características: Schemas Pydantic v2, JWT Auth, OCR, Base de Datos         ║
    ║                                                                              ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_dependencies():
    """Verificar dependencias del sistema"""
    logger.info("Verificando dependencias...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'pydantic',
        'python-jose',
        'passlib',
        'python-multipart'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            logger.info(f"✅ {package} - OK")
        except ImportError:
            missing_packages.append(package)
            logger.error(f"❌ {package} - FALTANTE")
    
    if missing_packages:
        logger.error(f"Paquetes faltantes: {', '.join(missing_packages)}")
        logger.info("Instale las dependencias con: pip install -r requirements.txt")
        return False
    
    logger.info("Todas las dependencias están instaladas correctamente")
    return True

def setup_directories():
    """Crear directorios necesarios"""
    logger.info("Configurando directorios del sistema...")
    
    directories = [
        'uploads',
        'outputs', 
        'data',
        'logs',
        'ssl'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"✅ Directorio '{directory}' - OK")
    
    # Verificar permisos de escritura
    test_file = 'logs/test_write.tmp'
    try:
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        logger.info("✅ Permisos de escritura - OK")
    except Exception as e:
        logger.error(f"❌ Error de permisos: {e}")
        return False
    
    return True

def setup_database():
    """Configurar base de datos"""
    logger.info("Configurando base de datos...")
    
    try:
        # Configurar SQLite
        os.environ["DATABASE_URL"] = "sqlite:///./data/documents.db"
        
        # Verificar que el directorio data existe
        os.makedirs('data', exist_ok=True)
        
        # Crear archivo de base de datos si no existe
        db_file = Path('data/documents.db')
        if not db_file.exists():
            db_file.touch()
            logger.info("✅ Archivo de base de datos creado")
        
        logger.info("✅ Base de datos SQLite configurada correctamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error configurando base de datos: {e}")
        return False

def run_migrations():
    """Ejecutar migraciones de base de datos"""
    logger.info("Ejecutando migraciones de base de datos...")
    
    try:
        # Agregar src al path
        sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
        
        # Importar y ejecutar migraciones
        from app.core.database import engine, Base
        from app.models.document import Document
        from app.models.user import User
        
        # Crear todas las tablas
        Base.metadata.create_all(bind=engine)
        
        logger.info("✅ Migraciones ejecutadas correctamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error ejecutando migraciones: {e}")
        return False

def start_server():
    """Iniciar servidor FastAPI"""
    logger.info("Iniciando servidor FastAPI...")
    
    try:
        # Comando para iniciar el servidor
        cmd = [
            sys.executable, '-m', 'uvicorn',
            'src.app.main:app',
            '--host', '0.0.0.0',
            '--port', '8000',
            '--reload',
            '--log-level', 'info'
        ]
        
        logger.info("🚀 Iniciando servidor en http://0.0.0.0:8000")
        logger.info("📚 Documentación disponible en http://0.0.0.0:8000/docs")
        logger.info("🔧 Panel de administración en http://0.0.0.0:8000/admin")
        logger.info("💡 Presione Ctrl+C para detener el servidor")
        
        # Ejecutar servidor
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        logger.info("🛑 Servidor detenido por el usuario")
    except Exception as e:
        logger.error(f"❌ Error iniciando servidor: {e}")
        return False
    
    return True

def main():
    """Función principal"""
    print_banner()
    
    logger.info("Iniciando sistema de producción...")
    
    # Verificaciones previas
    if not check_dependencies():
        logger.error("❌ Faltan dependencias. Instale los paquetes requeridos.")
        sys.exit(1)
    
    if not setup_directories():
        logger.error("❌ Error configurando directorios.")
        sys.exit(1)
    
    if not setup_database():
        logger.error("❌ Error configurando base de datos.")
        sys.exit(1)
    
    if not run_migrations():
        logger.error("❌ Error ejecutando migraciones.")
        sys.exit(1)
    
    logger.info("✅ Sistema configurado correctamente")
    logger.info("🎯 Iniciando servidor de producción...")
    
    # Iniciar servidor
    start_server()

if __name__ == "__main__":
    main()











